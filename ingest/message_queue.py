"""
Module to help with drainable multiprocess aware message queue
"""

from multiprocessing import Event, Queue
from multiprocessing.managers import BaseManager
from queue import Empty
from typing import Any, List

from .debugging import app_logger as log

class QueueWrapper(object):

    def __init__(self, name: str, q: Queue = None, preventive_writes: Event = None):
        self.name: str = name