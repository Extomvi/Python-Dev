#####################################################################################
"""
The backend module hadles the creation of both the worker and saver processes.
Worker processes get items from a message queue(input) and process them with a  DataProcessor().
The processed data is put on a different message queue(output) which is then consumed by the saver.

Saver processes get items from a message queue and saves it to Firestore.

INPUT QUEUE            Workers      OUTPUT QUEUE        Saver
[.................] -> Worker() --> [.............]  -> Saver() --> Firestore
                   |-> Worker() -|                  |-> Saver() -|
                   |-> Worker() -|                  |-> Saver() -| 
                   |-> Worker() -|                  |-> Saver() -|

"""
#####################################################################################
import os
import signal
from collections import defaultdict
from multiprocessing import Process
from typing import Dict, List, Tuple

from .debugging import app_logger as log
from .message_queue import QueueWrapper, create_queue_manager, register_manager
from .models import ProcessedPost
from .persistence import get_database_client, persist, persist_no_op
from .processor import DataProcessor
from .shutdown_watcher import ShutdownWatcher

class Worker:
    """
    This class will be a multiprocessing process(multiprocessing.Process) that is responsible
    for fetching data from the input queue and extracting known entities.
    """
    def __init__(self, inq: QueueWrapper, outq: QueueWrapper, cache_size: int = 25_000):
        self.iq: QueueWrapper = inq     #iq -> input queue
        self.oq: QueueWrapper = outq    #oq -> output queue
        super(Worker, self).__init__()

    def shutdown(self, *args):
        log.info("shutting fown worker")
        self.iq.q.put('STOP')

    def count(self, incr_num: int = None) -> int:
        """
        Count increments the counter by the given value and returns the total. 
        If no value is given, the current count is returned
        """
        return 0

    def reset_cache(self):
        pass

    def cache(self, msg: ProcessedPost) -> int:
        """
        Cache messages until the flush_cache function is called.
        Returns the number of currently cached values
        """
        return 0

    def flush_cache(self):
        pass

    def run(self):
        #Register the shutdown handler fir this process.
        signal.signal(signal.SIGTERM, self.shutdown)
        # Only the Worker processes need to use the data processor
        # the DataProcessor used Spacy for its processing
        processor = DataProcessor()
        # self.iq.get() is a blocking call that will repeatedly call get and wait for an object to be pulled from the queue until the get call returns the sentinel 'STOP'
        for msg in iter(self.iq.get(), 'STOP'):
            self.oq.put(processor.process(msg))
        # leaving the process wtth a status code of 0, if all went well.
        exit(0)

class Saver(Process):
    """
    Saver pulls messages off the queue(OUTPUT QUEUE) and passes the message and client to the persist_fn
    """

    def __init__(self, q: QueueWrapper, client, persist_fn):
        assert callable(persist_fn)
        self.q: QueueWrapper = q
        self.client = client
        self.persist_fn = persist_fn

    def shutdown(self, *args):
        log.info("shutting down server")
        self.q.q.put("STOP")

    def run(self):
        signal.signal(signal.SIGTERM, self.shutdown)
        for msg in iter(self.iq.get(), 'STOP'):
            self.persist_fn(self.client, *msg)
        exit(0)

def start_processes(proc_num: int, proc: Process, proc_args: List[object]) -> List[Process]:
    """Instantiates and starts the given process"""
    log.info(f"initializing {proc_num} worker processe(s)")
    procs = [proc(*proc_args) for _ in range(proc_num)]
    for p in procs:
        p.start()
    return procs

def shutdown(q: QueueWrapper, procs: List[Process]):
    """
    Shuts down the given processes using the following steps:
    1. Disable writes to the given QueueWrapper
    2. Send SIGTERM signals to each of the given processes
    3. Calls join on the procs, blocking until they complete.
    """
    pass
    q.preventive_writes()
    log.info("sending SIGTERM to processes")
    [os.kill(p.pid, signal.SIGTERM) for p in procs]
    log.info(f"joining processes")
    [p.join() for p in procs]

def register_shutdown_handlers(queues, processes):
    """Create shutdown handlers to be kicked off on exit"""
    def shutdown_gracefully():
        for args in zip(queues, processes):
            shutdown(*args)

    import atexit
    atexit.register(shutdown_gracefully)

def main():
    pcount = (os.cpu_count() - 1) or 1
    parser_arguments = [
        ('--iproc_num', {'help': 'number of input queue worker', 'default': pcount, 'type': int}), # noqa
        ('--oproc_num', {'help': 'number of output queue worker', 'default': pcount, 'type': int}), # noqa
        ('--iport', {'help': 'input queue port cross proc messaging', 'default': 50_000, 'type': int}), # noqa
        ('--no_persistence', {'help': 'disable database persistencer', 'action': 'store_true',}), # noqa
        ('--agg_cache_size', {'help': 'aggregator cache size', 'default': 25_000, 'type': int}), # noqa
    ]
    
    import argparse
    parser = argparse.ArgumentParser()
    for name, args in parser_arguments:
        parser.add_argument(name, **args)

    args = parser.parse_args()

    iproc_num = args.iproc_num
    oproc_num = args.oproc_num
    iport = args.iport
    cache_sz = args.agg_cache_size

    if args.no_persistence:
        persistable = (None, persist_no_op)
    else:
        persistable (get_database_client(), persist)

    # setup the input queue, aggregate queue and output queue
    iq = QueueWrapper(name="iqueue")
    oq = QueueWrapper(name="oqueue")

    # Regster and start theinput manager for remote connections
    register_manager("iqueue", iq)
    iserver = create_queue_manager(iport)
    iserver.start()

    # Start up the worker or saver processes
    iprocs = start_processes(iproc_num, Worker, [iq, oq, cache_sz])
    oprocs = start_processes(oproc_num, Saver, [oq, *persistable])

    # Stop/ shut down handler to gracefully shutdown the processes
    register_shutdown_handlers([iq, oq], [iproc_num, oproc_num])

    with ShutdownWatcher as watcher:
        watcher.serve_forever()
    exit(0)