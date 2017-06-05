From Iterators to asyncio, Part I: Generators
=============================================

:slug: from_iterators_to_asyncio_part_i
:date: 2015-05-20 12:00
:categories: Articles
:tags: Python, generators
:status: draft

:summary: Introduction


The rise of iterators
---------------------

Let's start with good-old **iterators**. In 2001, iterators were
introduced to Python 2.2 via PEP 234 [1]_. What are they used
for? Imagine a simple ``for`` loop:

.. code-block:: python

   for i in range(0, 10):
       print(x)

Quiet simple, isn't it? What if you want to iterate over a dynamic
sequence, like *Fibonacci sequence*: ``0, 1, 1, 2, 3, 5, 8, ...``
as follows?

.. code-block:: python

   for i in FibonacciRange():
       print(i)

That is where iterators join the play. An iterator is an object
with defined ``__iter__()`` and ``__next__()`` (``next()`` in
Python 2.x) methods:

.. code-block:: python

  class FibonacciRange:
      def __iter__(self):
          self.a = 0
          self.b = 1
          return self

      def __next__(self):
          ret = self.a
          self.a, self.b = self.b, self.a + self.b
          return ret

When Python reaches the ``for .. in X`` statement it calls
``iter(X)`` which invokes the ``__iter__()`` method of the
object ``X``. The ``__iter__`` method should return
an Iterator object, which is almost always, itself. Then
``next(X)`` is called each time before proceeding into the
body of the loop. I believe you have already suggested that
``next(X)`` invokes ``X.__next__()``. And that is correct!

So, iterators are extremely handy when you need something more than
a simple range and want to hide all the logic of the returned
values. For example:

.. code-block:: python

   for pixel in image:
       ...

   for record in database_table:
       ...

   for article in blog:
       ...

Compare this to a code which was written before iterators:

.. code-block:: python

  for i in range(0, image.pixels.count):
      pixel = image.pixels[i]
      ...

No need to say, that iterators improve the code readability remarkably.

Finally, what happens when there are no items left in the iterator?
For example, when all records of the database have been processed?
The ``next(X)`` call raises a ``StopIteration`` exception,
which signals the for loop that iteration is over.

Let's simulate a ``for`` loop iteration over a list by using ``while``:

.. code-block:: python

  fib = [0, 1, 1, 2, 3, 5]
  fib_iter = iter(fib)

  while True:
      try:
          x = next(fib)
          print(x)
      except StopIteration:
          break

As you have already imagined, the ``for`` version is much shorter
and cleaner:

.. code-block:: python

  fib = [0, 1, 1, 2, 3, 5]
  for x in fib:
      print(x)

But that is not all! Even an experienced pythonista may not know that
``iter()`` function can be used as ``iter(callable, sentinel) -> iterator``.
In this form, the ``callable`` is called until it returns the ``sentinel``.
For example, the following code creates an iterator, which returns random
numbers in [0..9] range, until the random generator generates ``"5"``:

.. code-block:: python

   import random

   for num in iter(lambda: random.randint(0, 9), 5)
       print(num)

   >>> 4
   >>> 9
   >>> 7
   >>> 7

Let's start with good-old **generators**. Generators appeared in
Python back in 2001 through PEP 255 [2]_. They came with the
new ``yield`` keyword

.. [1] https://www.python.org/dev/peps/pep-0234/
.. [2] https://www.python.org/dev/peps/pep-0255/
