#!/usr/bin/env python
# encoding: utf-8

from collections import namedtuple

from ycyc.base.contextutils import catch
from ycyc.base.typeutils import SimpleExceptions

EventsExceptions = SimpleExceptions()
ListenerDuplicatedError = EventsExceptions.ListenerDuplicatedError
ListenerNoExistedError = EventsExceptions.ListenerNoExistedError
EventNoExistedError = EventsExceptions.EventNoExistedError


class Event(object):
    CallbackResult = namedtuple("CallbackResult", [
        "callback", "result", "exception",
    ])

    def __init__(self):
        super(Event, self).__init__()
        self.callbacks = []

    def register(self, callback):
        """
        Register a callback to this event
        """
        if callback in self.callbacks:
            raise ListenerDuplicatedError()
        self.callbacks.append(callback)
        return callback

    def unregister(self, callback):
        """
        Unregister a callback from this event
        """
        if callback not in self.callbacks:
            raise ListenerNoExistedError()
        self.callbacks.remove(callback)
        return callback

    def notify_iter(self, sender, args=None, kwargs=None):
        args = args or tuple()
        kwargs = kwargs or dict()

        for callback in self.callbacks:
            try:
                exception = None
                result = callback(sender, *args, **kwargs)
            except Exception as exception:
                result = None

            yield self.CallbackResult(
                callback=callback, result=result,
                exception=exception,
            )

    def notify(self, sender, *args, **kwargs):
        """
        Notify the listeners when event is happending,
        but stop if catch a exception.
        """
        for i in self.notify_iter(sender, *args, **kwargs):
            if i.exception:
                raise i.exception

    def notify_all(self, sender, *args, **kwargs):
        """
        Notify all the listeners when event is happending.
        """
        return [
            i for i in self.notify_iter(sender, *args, **kwargs)
        ]


class EventsCenter(dict):
    """
    Event center to manage some events as a dict
    """
    def __init__(self, event_factory=None):
        super(EventsCenter, self).__init__()
        self.event_factory = event_factory or Event

    def __missing__(self, name):
        event = self[name] = self.event_factory()
        return event
