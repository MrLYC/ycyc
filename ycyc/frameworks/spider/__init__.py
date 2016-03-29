#!/usr/bin/env python
# encoding: utf-8

import functools
import logging

import requests

from ycyc.base.decoratorutils import cachedproperty
from ycyc.base.iterutils import dict_merge
from ycyc.base.lazyutils import lazy_import

pyquery = lazy_import("pyquery")
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

    def parse_form_data(self, selector="form:first"):
        data = {}
        form_node = self.selector.find(selector)  # pylint: disable=E1101
        for i in form_node.find("input"):
            input_node = pyquery.PyQuery(i)
            name = input_node.attr("name")
            type_ = input_node.attr("type")
            if not name or type_ in ["submit", "button"]:
                continue
            data[name] = input_node.val()
        return data

    def make_links_absolute(self):
        self.selector.make_links_absolute(  # pylint: disable=E1101
            self.raw_response.url
        )


class AsyncSpider(object):

    def __init__(self, target=None, opener=None, worker=None, headers=()):
        self.worker = worker or self.worker_factory()
        self.opener = opener or requests.Session()
        self.target = target
        self.default_headers = dict(headers)

    def on_request(self, request):
        logger.debug("Spider on_request, url: %s", request.url)
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
            "Spider on_response, url: %s, status: %s, reason: %s",
            response.url, response.status_code, response.reason,
        )
        real_response = Response(request, response)
        self.add_tasks(callback(real_response))

    def add_tasks(self, requests):
        for request in requests or ():
            logger.debug("Spider add a new task: %s", request.url)
            request.headers = dict_merge((request.headers, self.default_headers))
            self.worker.apply_async(
                self.on_request,
                args=(request,),
            )

    def start(self):
        logger.info("Spider start to run")
        requests = self.run()
        self.add_tasks(requests)

    def join(self):
        logger.info("Spider start to join")
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
