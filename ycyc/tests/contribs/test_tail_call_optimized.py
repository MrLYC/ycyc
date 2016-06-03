#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from ycyc.contribs.tail_call_optimized import tail_call_optimized


class TestTailCallOptimized(TestCase):
    def test_usage(self):
        @tail_call_optimized
        def factorial(n, acc=1):
            "calculate a factorial"
            if n == 0:
                return acc
            return factorial(n - 1, n * acc)

        factorial(10000)

        @tail_call_optimized
        def fib(i, current=0, next=1):
            if i == 0:
                return current
            else:
                return fib(i - 1, next, current + next)

        fib(10000)
