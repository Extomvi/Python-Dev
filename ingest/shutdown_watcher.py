"""
Module that provides a method for blocking until an OS signal is sent
"""

import signal
import time
from .debugging import app_logger as log

class ShutdownWatcher:
    """
    This listens for signals: SIGINT and SIGTERM.
    When the app is signaled to shutdown, it sets should_continue to False.

    Example:

    with ShutdownWatcher() as watcher:
        watcher.serve)forever() # <-- Blocks until signaled
    """

    def __init__(self) -> None:
        self.should_continue = True

        for s in [signal.SIGTERM, signal.SIGINT]:
            signal.signal(s, self.exit)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.exit()

    def serve_forever(self):
        while self.should_continue:
            time.sleep(0.1)

    def exit(self, *args, **kwargs):
        self.should_continue = False