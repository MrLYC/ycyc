#!/usr/bin/env python
# encoding: utf-8

from contextlib import contextmanager


class StateNotAllowError(Exception):
    pass


class EndOfSequenceStateError(Exception):
    pass


class SequenceStateFinishedError(Exception):
    pass


class FreeState(object):
    def __init__(self, init_state):
        self.last_state = None
        self.state = init_state
        self.exception = None

    def check_is_in_states(self, states):
        if self.state not in states:
            raise StateNotAllowError("%s not allow" % self.state)

    def state_to(self, to_state):
        self.last_state = self.state
        self.state = to_state

    def on_success(self, allow_states, success_state):
        self.check_is_in_states(allow_states)
        self.state_to(success_state)
        self.exception = None

    def on_fail(self, allow_states, fail_state, exception):
        self.check_is_in_states(allow_states)
        self.state_to(fail_state)
        self.exception = exception

    @contextmanager
    def processing(self, allow_states, success_state, fail_state):
        if not isinstance(allow_states, (tuple, list, set)):
            allow_states = (allow_states,)

        self.check_is_in_states(allow_states)
        try:
            yield
        except Exception as err:
            self.on_fail(allow_states, fail_state, err)
            raise
        else:
            self.on_success(allow_states, success_state)


class SequenceState(FreeState):
    __SequenceStates__ = ()
    __FailState__ = "error"

    def __init__(self, fail_state=NotImplemented):
        if fail_state is not NotImplemented:
            self.__FailState__ = fail_state
        self.index = 0
        self.base = super(SequenceState, self)
        self.base.__init__(init_state=self.__SequenceStates__[self.index])

    @property
    def next_state(self):
        index = self.index + 1
        if index >= len(self.__SequenceStates__):
            raise EndOfSequenceStateError()
        return self.__SequenceStates__[index]

    @property
    def is_finished(self):
        if not self.index < len(self.__SequenceStates__):
            return True
        if self.state is self.__FailState__:
            return True
        return False

    def on_success(self, allow_states, success_state):
        self.base.on_success(allow_states, success_state)
        self.index += 1

    def processing(self, allow_states=None):
        if self.is_finished:
            raise SequenceStateFinishedError()
        if allow_states is None:
            allow_states = self.state

        return self.base.processing(
            allow_states, self.next_state, self.__FailState__,
        )


class QSequenceState(SequenceState):
    def __init__(self, states, fail_state=NotImplemented):
        self.__SequenceStates__ = states
        super(QSequenceState, self).__init__(fail_state=fail_state)


def SequenceStateBuilder(sequence_states, fail_state=NotImplemented):
    class NewSequenceState(SequenceState):
        __SequenceStates__ = sequence_states
        if fail_state is not NotImplemented:
            __FailState__ = fail_state

    return NewSequenceState
