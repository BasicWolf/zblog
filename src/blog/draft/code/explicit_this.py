#!/usr/bin/python3

def add_this(f):
    def wrapped(self, *args, **kwargs):
        f.__globals__['this'] = self
        return f(*args, **kwargs)
    return wrapped


class C:
    name = 'Alex'

    @add_this
    def say(phrase):
        print("{} says: {}".format(this.name, phrase))

c = C()
c.say('Can you believe it? There is no `self` here!')

import types

class AddThisMeta(type):
    def __new__(cls, name, bases, classdict):
        new_classdict = {
            key: add_this(val) if isinstance(val, types.FunctionType) else val
            for key, val in classdict.items()
        }
        new_class = type.__new__(cls, name, bases, new_classdict)
        return new_class


class D(metaclass=AddThisMeta):
    name = 'Daniel'

    def say(phrase):
        print("{} says: {}".format(this.name, phrase))

    def run():
        print("{} runs away :)".format(this.name))

d = D()
d.say('And now, there is only AddThisMeta!')
d.run()
