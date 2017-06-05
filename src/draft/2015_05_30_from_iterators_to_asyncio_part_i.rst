From Iterators to asyncio, Part I: Generators
=============================================

:slug: from_iterators_to_asyncio_part_i
:date: 2015-05-30 12:00
:categories: Articles
:tags: Python, programming
:summary: Summary



From Iterators to Generators
----------------------------

**Note:** if you are an experienced Python programmer, this part
might be rather boring :)

Iterators were introduced to Python 2.2 back in 2001 through PEP 234 [*]_.
They helped Python to make a leap from simple ``for`` loops like:

.. code-block:: python

   for i in range(0, 10):
       print(x)

To generic way of sequentially processing any kind of containers or data streams.
For example, consider a *Fibonacci sequence*: ``0, 1, 1, 2, 3, 5, 8, ...``:

.. code-block:: python

   for i in FibonacciRange():
       print(i)

Here ``FibonacciRange`` implements iterator interface.
Basically, an iterator is an object with defined
``__iter__()`` and ``__next__()`` methods:

.. code-block:: python

  class FibonacciRange:
      def __iter__(self):
          self.a = 0
          self.b = 1
          return self

      # next() in Python 2.x
      def __next__(self):
          ret = self.a
          self.a, self.b = self.b, self.a + self.b
          return ret

When Python reaches the ``for .. in X`` statement it calls
``iter(X)`` which invokes the ``__iter__()`` method of the
object ``X``. The ``__iter__`` method should return
an ``Iterator`` object, which is almost always, itself. Then
``next(X)`` is called each time before proceeding into the
body of the loop. I believe you have already suggested that
``next(X)`` invokes ``X.__next__()``. And that is correct!

So, Iterators are extremely handy when you need something more than
a simple range and want to hide all the logic of the returned
values. For example:

.. code-block:: python

   for line in file:
       ...

   for pixel in image:
       ...

   for record in database_table:
       ...

   for article in blog:
       ...


Compare this to a code which was written before iterators:

.. code-block:: python

  for i in range(0, image.get_pixels_count()):
      pixel = image.get_pixel(i)
      ...

No need to say, that iterators remarkably improve the code readability.

Finally, what happens when there are no items left in the iterator?
For example, when all records of the database have been processed?
The iterator object raises ``StopIteration`` exception on the following
``next(X)`` call. It signals that iteration is over.

It can be easily demonstrated by simulating a ``for`` loop iteration
over a list by using ``while``:

.. code-block:: python

  fib = [0, 1, 1, 2, 3, 5]
  fib_iter = iter(fib)

  while 1:  # loop forever
      try:
          x = next(fib)
          print(x)
      expect StopIteration:
          print('Finished iterating')

Let's start with good-old **generators**. Generators appeared in
Python back in 2001 through PEP 255 [*]_. They came with the
new ``yield`` keyword

.. [*] https://www.python.org/dev/peps/pep-0234/
.. [*] https://www.python.org/dev/peps/pep-0255/
