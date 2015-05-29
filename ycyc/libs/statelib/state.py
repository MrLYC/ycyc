#!/usr/bin/env python
# encoding: utf-8

from contextlib import contextmanager


class StateNotAllowError(Exception):
    pass


class FreeState(object):
    def __init__(self, init_state):
        self.from_state = None
        self.state = init_state
        self.exception = None

    def is_in_states(self, states):
        if self.state not in states:
            raise StateNotAllowError("%s not allow" % self.state)

    def state_to(self, to_state):
        self.from_state = self.state
        self.state = to_state

    @contextmanager
    def processing(self, allow_states, success_state, fail_state):
        if not isinstance(allow_states, (tuple, list, set)):
            allow_states = (allow_states,)

        self.is_in_states(allow_states)
        try:
            yield
        except Exception as err:
            self.is_in_states(allow_states)
            self.state_to(fail_state)
            self.exception = err
            raise
        else:
            self.is_in_states(allow_states)
            self.state_to(success_state)
            self.exception = None
