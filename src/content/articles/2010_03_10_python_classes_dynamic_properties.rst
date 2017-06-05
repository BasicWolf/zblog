Python classes: Dynamic properties
==================================

:slug: python_classes_dynamic_properties
:date: 2010-03-10 12:00
:categories: Articles
:tags: programming, Python

:summary: Python never stops surprising me. While doing my master IT project, I was looking for a way to add dynamic properties to classes (we're speaking of new-style classes of course!). I did a little research and here are the results...


I love Python 3
---------------

Even Python 2.x is still used everywhere, it is time to move to Python 3.
I made the code fully Python2.6 - compatible, but if you'd like to have a
nice output of print(..) function please use the

.. code-block:: python

  from __future__ import print_function

statement.


A simple class
--------------

This is a simple class with one property:

.. code-block:: python

  class Man(object):
      def __init__(self, name):
          self._name = name

      @property
      def name(self):
          return self._name

      @name.setter
      def name(self, value):
          self._name = value

      m = Man('Alex Black')
      print(m.name)

      m.name = 'Kyra Brown'
      print(m.name)


The output is:

.. code-block:: none

  Alex Black
  Kyra Brown


We keep the local values in attributes that start with the underscore,
e.g. self._name. Usually this is a way I separate "private" and "public"
members of a class/object [1]_ (of course this "private" members remain
"public").

This code does the same as the code above:

.. code-block:: python

  class Man(object):
      def __init__(self, name):
          self._name = name

      def _name_get(self):
          return getattr(self, '_name')

      def _name_set(self, value):
          setattr(self, '_name', value)

      name = property(fget = _name_get, fset = _name_set)



There are two core changes:

1. The ``_name`` attribute of an object is read and set by the ``getattr(..)``
   and ``setattr(..)`` functions.
2. The ``@property`` decorator is replaced by the built-in ``property(...)``
   function [2]_ (which is actually "behind" that decorator).

Dynamic properties class
------------------------
Finally, let's write a class called "Properties" that will allow adding dynamic
properties. The properties will require local ("private") fields. We can use
the same scheme as above, e.g. for property name, the private member of a
class is ``_name``:


.. code-block:: python

  class Properties(object):
      def add_property(self, name, value):
          # create local fget and fset functions
          fget = lambda self: self._get_property(name)
          fset = lambda self, value: self._set_property(name, value)

          # add property to self
          setattr(self.__class__, name, property(fget, fset))
          # add corresponding local variable
          setattr(self, '_' + name, value)


      def _set_property(self, name, value):
          setattr(self, '_' + name, value)

      def _get_property(self, name):
          return getattr(self, '_' + name)

The trick in ``add_property(..)`` is that we create two lambda objects (those
could also be anonymous functions) which use the ``self._get_property`` and
``self._set_property`` methods with particular value of name argument.

Let's play with this class:

.. code-block:: python

  po = Properties()
  po.add_property('user', 'noname')
  po.add_property('speed', 50)

  print(po.user, po.speed)

  po.speed = 100
  po.name = 'Alex Black'

  print(po.user, po.speed)
  print(po._user, po._speed)


The output is:

.. code-block:: none

  noname 50
  Alex Black 100
  Alex Black 100



A practical usage
-----------------

After all, what is a practical usage of dynamic properties? I'm sure you
may have thought of that if you're reading this post now :) Here is a small
example of a class which is able to "lock" the properties' setters:

.. code-block:: python


  class PropertiesWithLock(object):
      def __init__(self, lock = False):
          self.lock = lock

      def add_property(self, name, value):
          fget = lambda self: self._get_property(name)
          fset = lambda self, value: self._set_property(name, value)

          setattr(self.__class__, name, property(fget, fset))
          setattr(self, '_' + name, value)


      def _set_property(self, name, value):
          if not self.lock:
              setattr(self, '_' + name, value)
          else:
               print('Cannot change "{0}": properties are locked'
                      .format(name))

      def _get_property(self, name):
          return getattr(self, '_' + name)

And the usage:

.. code-block:: python

  po = PropertiesWithLock()
  po.add_property('user', 'noname')
  po.add_property('speed', 50)

  print(po.user, po.speed)
  >>> noname 50

  po.user = 'a user'
  po.speed = 200
  print(po.speed)
  >>> a user 200

  po.lock = True
  po.user = 'a user'
  >>> Cannot change "user": properties are locked




References
----------
.. [1] `Reserved classes of identifiers
       <http://docs.python.org/reference/lexical_analysis.html#reserved-classes-of-identifiers>`_
.. [2] `property([fget[, fset[, fdel[, doc]]]])
       <http://docs.python.org/library/functions.html#property>`_
