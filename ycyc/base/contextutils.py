#!/usr/bin/env python
# encoding: utf-8

from contextlib import contextmanager
import six
import logging
import threading
import time

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
def companion(
    target, auto_start=True, auto_join=True, process=threading.Thread,
):
    """
    Run the target function as block companion.
    :param target: callable object
    :param auto_start: start thread immediately
    :param auto_join: join thread when exit
    """
    processor = process(target=target)
    processor.daemon = True
    if auto_start:
        processor.start()
    try:
        yield processor
    finally:
        if processor.is_alive():
            processor.join()


@contextmanager
def timeout(seconds, interval=None, ticks=None):
    """
    Send KeyboardInterrupt to main thread to terminate it and
    convert it as RuntimeError if timeout.
    :param seconds: timeout seconds
    :param interval: poll interval
    :param ticks: CPU-Bound thread check interval
    """
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

    with companion(poll_signal, auto_start=False) as poll_thread:
        if seconds > 0:
            poll_thread.start()

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


@contextmanager
def heartbeat(target, interval, auto_start=True, auto_join=True):
    """
    Run target as heartbeat.
    :param target: callable object
    :param interval: sleep interval
    :param auto_start: start thread immediately
    :param auto_join: join thread when exit
    """
    enable = True

    def check():
        while enable:
            target()
            time.sleep(interval)

    with companion(
        check, auto_start=auto_start, auto_join=auto_join,
    ) as processor:
        try:
            yield processor
        finally:
            enable = False
