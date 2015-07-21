#!/usr/bin/env python
# encoding: utf-8

from ycyc.base.typeutils import SimpleExceptions

SimpleExceptions = SimpleExceptions()
OperateError = SimpleExceptions.OperateError
RangeError = SimpleExceptions.RangeError
EmptyRange = None


class ARange(object):
    def __init__(self, start, end, include_start=True, include_end=True):
        if end < start:
            raise RangeError

        self.start = start
        self.end = end
        self.include_start = bool(include_start)
        self.include_end = bool(include_end)

    def __str__(self):
        return "{lb}{start}..{end}{rb}".format(
            lb="[" if self.include_start else "(",
            start=self.start, end=self.end,
            rb="]" if self.include_end else ")",
        )

    def __repr__(self):
        return (
            "{clsname}({start}, {end}, "
            "include_start={include_start}, include_end={include_end})"
        ).format(
            clsname=self.__class__.__name__,
            start=repr(self.start),
            end=repr(self.end),
            include_start=repr(self.include_start),
            include_end=repr(self.include_end),
        )

    def __contains__(self, point):
        if point is None:
            return False

        if self.start < point < self.end:
            return True
        if self.include_start and point == self.start:
            return True
        if self.include_end and point == self.end:
            return True
        return False

    def __and__(self, other):
        if self.start > other.end:
            return EmptyRange
        if self.end < other.start:
            return EmptyRange

        if other.start in self:
            start = other.start
            include_start = other.include_start
        elif self.start in other:
            start = self.start
            include_start = self.include_start
        else:
            raise OperateError

        if other.end in self:
            end = other.end
            include_end = other.include_end
        elif self.end in other:
            end = self.end
            include_end = self.include_end
        else:
            raise OperateError

        return ARange(start, end, include_start, include_end)

    def __add__(self, other):
        return ARange(
            self.start + other.start,
            self.end + other.end,
            include_start=self.include_start and other.include_start,
            include_end=self.include_end and other.include_end,
        )

    def __sub__(self, other):
        return ARange(
            self.start - other.start,
            self.end - other.end,
            include_start=self.include_start and other.include_start,
            include_end=self.include_end and other.include_end,
        )

    def __mul__(self, other):
        vals = [
            self.start * other.start,
            self.start * other.end,
            self.end * other.start,
            self.end * other.end,
        ]
        return ARange(
            min(vals),
            max(vals),
            include_start=self.include_start and other.include_start,
            include_end=self.include_end and other.include_end,
        )

    def is_after_of(self, point):
        if point < self.start:
            return True
        if not self.include_start and self.start == point:
            return True
        return False

    def is_before_of(self, point):
        if point > self.end:
            return True
        if not self.include_end and self.end == point:
            return True
        return False

    def has_sub_range(self, other):
        if self.is_after_of(other.start):
            if other.start != self.start or other.include_start:
                return False
        if self.is_before_of(other.end):
            if other.end != self.end or other.include_end:
                return False
        return True

    def is_follow_by(self, other):
        if self.end != other.start:
            return False
        if self.include_end == other.include_start:
            return False
        return True

    def sampling(self, step):
        val = self.start if self.include_start else self.start + step
        include_end = self.include_end
        end = self.end

        while val < end:
            yield val
            val += step

        if val == end and include_end:
            yield val
