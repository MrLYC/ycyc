#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from ycyc.libs.statelib.state import (
    FreeState, SequenceState, QSequenceState,
    StateNotAllowError, EndOfSequenceStateError, SequenceStateFinishedError,
)


class TestFreeState(TestCase):
    def test_usage(self):
        state = FreeState("init")
        self.assertEqual(state.state, "init")
        self.assertEqual(state.exception, None)
        self.assertEqual(state.last_state, None)

        with state.processing("init", "state1", "error1"):
            pass
        self.assertEqual(state.state, "state1")
        self.assertEqual(state.exception, None)
        self.assertEqual(state.last_state, "init")

        with self.assertRaises(StateNotAllowError):
            with state.processing("nothing", "", ""):
                pass
        self.assertEqual(state.state, "state1")
        self.assertEqual(state.exception, None)
        self.assertEqual(state.last_state, "init")

        with self.assertRaises(ValueError):
            with state.processing("state1", "state2", "error2"):
                raise ValueError()
        self.assertEqual(state.state, "error2")
        self.assertIsInstance(state.exception, ValueError)
        self.assertEqual(state.last_state, "state1")

        with state.processing(("error2", "state3"), "state3", "error3"):
            pass
        self.assertEqual(state.state, "state3")
        self.assertEqual(state.exception, None)
        self.assertEqual(state.last_state, "error2")

        with state.processing(("error2", "state3"), "state4", "error4"):
            pass
        self.assertEqual(state.state, "state4")
        self.assertEqual(state.exception, None)
        self.assertEqual(state.last_state, "state3")

class TestSequenceState(TestCase):
    def test_usage(self):
        class TSequenceState(SequenceState):
            __SequenceStates__ = ("init", "state1", "state2", "state3")

        state = TSequenceState()
        self.assertEqual(state.state, "init")
        self.assertEqual(state.index, 0)
        self.assertEqual(state.exception, None)
        self.assertEqual(state.last_state, None)
        self.assertEqual(state.next_state, "state1")
        self.assertEqual(state.is_finished, False)

        with state.processing():
            pass
        self.assertEqual(state.state, "state1")
        self.assertEqual(state.index, 1)
        self.assertEqual(state.exception, None)
        self.assertEqual(state.last_state, "init")
        self.assertEqual(state.next_state, "state2")
        self.assertEqual(state.is_finished, False)

        with state.processing():
            pass
        self.assertEqual(state.state, "state2")
        self.assertEqual(state.index, 2)
        self.assertEqual(state.exception, None)
        self.assertEqual(state.last_state, "state1")
        self.assertEqual(state.next_state, "state3")
        self.assertEqual(state.is_finished, False)

        with self.assertRaises(ValueError):
            with state.processing():
                raise ValueError()
        self.assertEqual(state.state, "error")
        self.assertEqual(state.index, 2)
        self.assertIsInstance(state.exception, ValueError)
        self.assertEqual(state.last_state, "state2")
        self.assertEqual(state.next_state, "state3")
        self.assertEqual(state.is_finished, True)

        with self.assertRaises(SequenceStateFinishedError):
            with state.processing():
                pass
        self.assertEqual(state.state, "error")
        self.assertEqual(state.index, 2)
        self.assertIsInstance(state.exception, ValueError)
        self.assertEqual(state.last_state, "state2")
        self.assertEqual(state.next_state, "state3")
        self.assertEqual(state.is_finished, True)
