#!/usr/bin/env python
# encoding: utf-8

import functools
import logging
from multiprocessing import pool

import requests
import pyquery

from ycyc.base.decoratorutils import cachedproperty
from ycyc.debug.decorators import debug_call_trace

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
    def __init__(self, raw_request, response):
        self.raw_response = response
        self.raw_request = raw_request

    def __getattr__(self, name):
        return getattr(self.raw_response, name)

    @cachedproperty
    def html(self):
        return self.raw_response.text

    @cachedproperty
    def selector(self):
        pq = pyquery.PyQuery(self.html)
        return pq

    def make_links_absolute(self):
        self.selector.make_links_absolute(self.raw_response.url)


class Spirder(object):
    def __init__(self, target=None, worker_factory=pool.ThreadPool):
        self.worker = worker_factory()
        self.session = requests.Session()
        self.target = target

    @debug_call_trace(logger)
    def on_request(self, request):
        self.worker.apply_async(
            self.session.send,
            args=(request.prepare(),),
            callback=functools.partial(
                self.on_response,
                request=request,
                callback=request.callback,
            ),
        )

    @debug_call_trace(logger)
    def on_response(self, response, request, callback):
        real_response = Response(request, response)
        self.add_tasks(callback(real_response))

    @debug_call_trace(logger)
    def add_tasks(self, requests):
        for request in requests or ():
            self.worker.apply_async(
                self.on_request,
                args=(request,),
            )

    @debug_call_trace(logger)
    def start(self):
        requests = self.start_request()
        self.add_tasks(requests)

    @debug_call_trace(logger)
    def stop(self):
        self.worker.close()
        self.worker.join()

    @debug_call_trace(logger)
    def start_request(self):
        if not callable(self.target):
            raise NotImplementedError
        return self.target()


def redirect_to(url, callback, **kwg):
    def redirect(response):
        yield Request(url=url, callback=callback, **kwg)
    return redirect


def save_to(path, data, mode="at"):
    with open(path, mode) as fp:
        fp.write(data)


def flow_return():
    raise StopIteration
