#!/usr/bin/env python
# encoding: utf-8

import functools
import logging

import requests

from ycyc.base.decoratorutils import cachedproperty

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
        import pyquery
        pq = pyquery.PyQuery(self.html)
        return pq

    def make_links_absolute(self):
        self.selector.make_links_absolute(self.raw_response.url)


class Spirder(object):
    def __init__(self, target=None, opener=None, worker=None):
        self.worker = worker or self.worker_factory()
        self.opener = opener or requests.Session()
        self.target = target

    def on_request(self, request):
        logger.debug("Spirder on_request, url: %s", request.url)
        self.worker.apply_async(
            self.opener.send,
            args=(request.prepare(),),
            callback=functools.partial(
                self.on_response,
                request=request,
                callback=request.callback,
            ),
        )

    def on_response(self, response, request, callback):
        logger.debug(
            "Spirder on_response, url: %s, status: %s, reason: %s",
            response.url, response.status_code, response.reason,
        )
        real_response = Response(request, response)
        self.add_tasks(callback(real_response))

    def add_tasks(self, requests):
        for request in requests or ():
            logger.debug("Spirder add a new task: %s", request.url)
            self.worker.apply_async(
                self.on_request,
                args=(request,),
            )

    def start(self):
        logger.info("Spirder start to run")
        requests = self.run()
        self.add_tasks(requests)

    def join(self):
        logger.info("Spirder start to join")
        if hasattr(self.worker, "close"):
            # for multiprocessing.pool
            self.worker.close()
        self.worker.join()

    def run(self):
        if not callable(self.target):
            raise NotImplementedError
        return self.target()

    @classmethod
    def worker_factory(cls):
        from multiprocessing.pool import ThreadPool
        return ThreadPool()


def redirect_to(url, callback, **kwg):
    def redirect(response):
        logger.info("redirect to %s", url)
        yield Request(url=url, callback=callback, **kwg)
    return redirect


def save_to(path, data, mode="ab"):
    with open(path, mode) as fp:
        fp.write(data)


def flow_return():
    raise StopIteration
