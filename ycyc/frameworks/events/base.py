#!/usr/bin/env python
# encoding: utf-8

from ycyc.base.contextutils import catch
from ycyc.base.typeutils import SimpleExceptions

EventsExceptions = SimpleExceptions()
ListenerDuplicatedError = EventsExceptions.ListenerDuplicatedError
ListenerNoExistedError = EventsExceptions.ListenerNoExistedError
EventNoExistedError = EventsExceptions.EventNoExistedError


class Event(object):
    def __init__(self):
        super(Event, self).__init__()
        self.listeners = []

    def notify(self, *args, **kwg):
        """
        Notify all the listeners that event is happended.
        """
        listeners = tuple(self.listeners)
        for listener in listeners:
            with catch():
                listener(*args, **kwg)

    def register(self, callback):
        """
        Register a callback to this event
        """
        if callback in self.listeners:
            raise ListenerDuplicatedError
        self.listeners.append(callback)

    def unregister(self, callback):
        """
        Unregister a callback from this event
        """
        with catch(ValueError, ListenerNoExistedError):
            self.listeners.remove(callback)


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
