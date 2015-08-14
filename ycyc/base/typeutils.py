#!/usr/bin/env python
# encoding: utf-8


def get_real_bases(bases):
    """
    Get real bases for types argument.
    >>> get_real_bases(None) #=> (object,)
    >>> get_real_bases(TypeA) #=> (TypeA,)
    >>> get_real_bases([TypeA, TypeB]) #=> (TypeA, TypeB)

    :param bases: type or type sequence
    """
    if bases is None:
        return (object,)
    if isinstance(bases, type):
        bases = (bases,)
    return tuple(bases)


def subtype(name, bases=None, attrs=None):
    """
    A easier way to create a type inherited from bases(default:object)
    with specified attrs.

    :param name: name of new type
    :param bases: bases class of new type
    :param attrs: class attributes of new type
    """
    return type(name, get_real_bases(bases), dict(attrs or {}))


class TypeFactory(object):
    """
    Create your type from this factory.
    >>> types_factory.NewType()
    equals:
    >>> subtype("NewType")
    """
    def __getattr__(self, name):
        return lambda bases=None, attrs=None: subtype(
            name, bases, attrs,
        )

types_factory = TypeFactory()


def subexception(name, bases=None, attrs=None):
    """
    A easier way to create an Exception

    :param name: name of new exception
    :param bases: bases class of new exception
    :param attrs: class attributes of new exception
    """
    return subtype(name, bases or [Exception], attrs)


class ExceptionFactory(object):
    """
    Create your type by this factory.
    >>> exceptions_factory.NewError()
    equals:
    >>> subexception("NewError")
    """
    def __getattr__(self, name):
        return lambda bases=None, attrs=None: subexception(
            name, bases, attrs,
        )

exceptions_factory = ExceptionFactory()


class SimpleExceptions(object):
    """
    Create and cached a simple exception.
    """
    def __getattr__(self, name):
        exception = subexception(name)
        setattr(self, name, exception)
        return exception


def freezed_attrs(attrs):
    """
    Decorator the declare attributes of cls is freezed.
    Attributes in attrs can only assigned once as
    initialization(usually is in __init__).

    :param attrs: attribute list
    """
    def setattr_hook(cls):
        def __setattr__(self, name, val):
            if name not in attrs or hasattr(self, name):
                raise AttributeError("attribute %s is not writable" % name)
            return super(cls, self).__setattr__(name, val)

        return subtype(
            cls.__name__, cls,
            {
                "__doc__": cls.__doc__,
                "__setattr__": __setattr__,
            }
        )
    return setattr_hook


class Constants(object):
    """
    The base class of constants
    """
    def __getitem__(self, key):
        return getattr(self, key)


def constants(**kwg):
    """
    Declare some constants.
    """
    @freezed_attrs(kwg.keys())
    class ConstantSet(Constants):
        def __init__(self):
            for k, v in kwg.items():
                setattr(self, k, v)

    return ConstantSet()
