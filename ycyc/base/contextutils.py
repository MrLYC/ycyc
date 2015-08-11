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
    exec_info = {
        "callback_returned": None,
        "exception": None,
        "ok": True,
    }
    try:
        yield exec_info
    except errors as err:
        exec_info["exception"] = err
        exec_info["ok"] = False
        if callback:
            exec_info["callback_returned"] = callback(err)
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
    processor = Popen(*args, **kwg)
    try:
        yield processor
    finally:
        if processor.poll() is None:
            processor.terminate()
            processor.wait()


@contextmanager
def timeout(seconds, interval=None, ticks=None):
    """
    Send KeyboardInterrupt to main thread to terminate it and
    convert it as RuntimeError if timeout.
    :param seconds: timeout seconds
    :param interval: poll interval
    :param ticks: CPU-Bound thread check interval
    """
    import threading
    import time
    import os
    import signal
    import sys

    signal_finished = False
    start = time.time()
    interval = interval or 0.1
    old_ticks = sys.getcheckinterval()

    cur_thread = threading.current_thread()
    assert cur_thread.name == "MainThread"

    def poll_signal():
        now = time.time()
        while not signal_finished and now - start < seconds:
            time.sleep(interval)
            now = time.time()
        if not signal_finished:
            os.kill(os.getpid(), signal.SIGINT)

    if seconds > 0:
        poll_thread = threading.Thread(target=poll_signal)
        poll_thread.daemon = True
        poll_thread.start()
    else:
        poll_thread = None

    if ticks is not None:
        sys.setcheckinterval(ticks)
    try:
        yield
    except KeyboardInterrupt:
        now = time.time()
        if now - start >= seconds > 0:
            raise RuntimeError("timeout")
        raise
    finally:
        signal_finished = True
        if ticks is not None:
            sys.setcheckinterval(old_ticks)
        if poll_thread and poll_thread.is_alive():
            poll_thread.join()


@contextmanager
def nothing(*args, **kwg):
    """
    Just a place holder.
    """
    yield


@contextmanager
def atlast(func, force=False):
    """
    Run func at last
    """
    try:
        yield
        func()
    except Exception:
        if force:
            func()
        raise
