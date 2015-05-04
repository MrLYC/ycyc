#!/usr/bin/env python
# encoding: utf-8

from contextlib import contextmanager
import six
import logging

logger = logging.getLogger(__name__)


@contextmanager
def catch(errors=Exception, reraise=None, callback=logger.warning):
    """
    A context manager to catch the exceptions raised from block.
    :param errors: exception or exceptions tuple
    :param reraise: reraise a new exception from catched exception(default: None)
    :param callback: callback when catched a exception(default: logger.warning)
    """
    try:
        yield
    except errors as err:
        if callback:
            callback(err)
        if reraise:
            six.raise_from(reraise, err)


@contextmanager
def subprocessor(*args, **kwg):
    """
    With new subprocess call,terminate it when exit context
    :param args: argument pass to subprocess.Popen
    :param kwg: key word argument pass to subprocess.Popen
    """
    from subprocess import Popen
    processor = None
    try:
        processor = Popen(*args, **kwg)
        yield processor
    finally:
        if processor.poll() is None:
            processor.terminate()
            processor.wait()


@contextmanager
def timeout(seconds):
    """
    Send KeyboardInterrupt to main thread to terminate it and
    convert it as RuntimeError if timeout.It's unreliable.
    :param seconds: timeout seconds
    """
    import thread
    import time

    signal_finished = False

    def poll_signal(seconds):
        now = start = time.time()
        while not signal_finished and now - start < seconds:
            time.sleep(0.1)
            now = time.time()
        if not signal_finished:
            thread.interrupt_main()
        print "Done"

    thread.start_new_thread(poll_signal, (seconds,))
    try:
        time.sleep(0)
        yield
        signal_finished = True
    except KeyboardInterrupt:
        raise RuntimeError("timeout")
