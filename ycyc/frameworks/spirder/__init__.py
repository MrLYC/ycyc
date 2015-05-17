#!/usr/bin/env python
# encoding: utf-8

import functools
import logging

import requests
import pyquery

from ycyc.base.decoratorutils import cachedproperty
from ycyc.base.contextutils import catch
from ycyc.debug import decorators

logger = logging.getLogger(__name__)


class Request(requests.Request):
    def __init__(
            self, url, callback, headers=None, params=None, data=None,
            json=None, method="GET", **kwg):
        super(Request, self).__init__(
            url=url, headers=headers, params=params, data=data, json=json,
            method=method, **kwg
        )
        self.callback = callback


class Response(object):
    def __init__(self, request, response):
        self.raw_request = request
        self.raw_response = response

    def __getattr__(self, name):
        return getattr(self.raw_response, name)

    @cachedproperty
    def html(self):
        return self.raw_response.text

    @cachedproperty
    def selector(self):
        pq = pyquery.PyQuery(self.html)
        pq.make_links_absolute(self.raw_response.url)
        return pq


class ThreadingSpirderWorker(object):
    def __init__(self, worker_cnt=5):
        try:
            from queue import Queue
        except ImportError:
            from Queue import Queue

        self.worker_cnt = worker_cnt
        self.task_quque = Queue(worker_cnt)
        self.threads = []
        self.enable = False

    @decorators.debug_call_trace(logger)
    def add_task(self, task):
        self.task_quque.put(task)

    @decorators.debug_call_trace(logger)
    def start(self):
        from threading import Thread

        def work():
            while self.enable:
                with catch():
                    task = self.task_quque.get()
                    result, callback = task()
                    callback(result)

        self.enable = True
        self.threads.extend([
            Thread(target=work) for i in range(self.worker_cnt)
        ])
        for thread in self.threads:
            thread.daemon = True
            thread.start()

    @decorators.debug_call_trace(logger)
    def stop(self):
        self.enable = False
        for thread in self.threads:
            thread.join()
            self.threads.remove(thread)


class Spirder(object):
    def __init__(self, worker_factory=ThreadingSpirderWorker):
        self.worker = worker_factory()
        self.session = requests.Session()

    @decorators.debug_call_trace(logger)
    def send(self, request):
        p_request = request.prepare()
        response = self.session.send(p_request)
        return Response(request, response), self.on_response

    @decorators.debug_call_trace(logger)
    def on_response(self, response):
        callback = response.raw_request.callback
        self.add_tasks(callback(response))

    @decorators.debug_call_trace(logger)
    def add_tasks(self, requests):
        for request in requests or ():
            self.worker.add_task(
                functools.partial(self.send, request)
            )

    @decorators.debug_call_trace(logger)
    def start(self):
        requests = self.start_request()
        self.add_tasks(requests)
        self.worker.start()

    @decorators.debug_call_trace(logger)
    def stop(self):
        self.worker.stop()

    def start_request(self):
        raise NotImplementedError

    def step_redirect(self, url, callback, **kwg):
        def redirect(response):
            yield Request(url=url, callback=callback, **kwg)
        return redirect

    def save_to(self, path, data, mode="wb"):
        with open(path, mode) as fp:
            fp.write(data)
