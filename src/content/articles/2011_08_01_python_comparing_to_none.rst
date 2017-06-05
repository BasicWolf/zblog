Python: comparing to None
=========================

:slug: python_comparing_to_none
:categories: Articles
:tags: programming, Python
:date: 2011-08-01 12:00

:summary: Python's documentation states that one has to use the ``is`` operator to compare a variable to ``None``. What happens when you avoid that advice?

Consider a class:

.. code-block:: python

  class Queue(object):
      def __init__(self):
          self._len = 0

      def __len__(self):
          return self._len

Next, the usage of the class is:

.. code-block:: python

  q = Queue()

  # at this point, you want to check if q is None
  if not q:
     doSomething()

The confusing thing is that ``doSomething()`` is actually called! And
that is because ``len(q) == 0``!

Instead, use the ``is None`` comparison:

.. code-block:: python

  if q is None:
      doSomething()
