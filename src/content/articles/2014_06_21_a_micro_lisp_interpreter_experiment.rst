A micro Lisp interpreter experiment
===================================

:slug: a_micro_lisp_interpreter_experiment
:categories: Articles
:tags: Python, Lisp, programming
:date: 2014-06-21 12:00

:summary: While reading the `Binary trees` chapter from `Programming Interviews Exposed <http://www.piexposed.com>`_ by John Mongan et al. I started thinking of alternative recursion examples which do not involve sorting, generating Fibonacci sequence, binary tree traversal and similar tasks. Lisp! Lisp is inseparable from recursion and Lisp interpreter would be a good case to demonstrate what recursion is and how it can be used efficiently. What would be a minimal simplified Lisp interpreter written in Python? Surprisingly, I managed to do it just in 6 lines of Python code! And this is not just because of Python being a wonderful language, but because of Lisp being such a beautiful and simple concept.

Let's define the language grammar and evaluation forms:

.. code-block:: none

  list := (item0, item1, ...)
  item := list | atom
  atom := stringliteral|numliteral

The evaluation rules are similar to any Lisp: the first atom is a function,
the rest - are the arguments:

.. code-block:: none

  fn = list[0]
  args = list[1:]

Notice that a list is written in a form of Python tuple. This is in a way
a cheat which allows decreasing the interpreter's code dramatically (i.e.
Python does the lexical and syntax analysis).
Also note that the interpreter does not include any built-in operators,
functions or special forms. They can all be created to extend the language
separately.

Let's write some examples before jumping to the code of the interpreter and
its extension functions:

.. code-block:: common-lisp

  (quote, 1, 2, 3) ; >>> (1, 2, 3)
  (plus, 1, 2, 3)  ; >>> 6
  (inc, 10)        ; >>> 11

Allright, enough sentimental talk, let's get to the interpreter!


The micro Lisp interpreter
--------------------------

.. code-block:: python

  def eval(list_or_atom):
      if isinstance(list_or_atom, tuple):
          fn, *fn_args = [eval(item) for item in list_or_atom]
          return fn(*fn_args)
      else:
          return list_or_atom


That is it! Here is how it works:
First, we check whether the input is a list (Python tuple) or an atom.
In case if it is an atom we return it immediately. Thus, ``eval(1)``
returns ``1``. If the argument is a tuple, we extract a function
as its first element, and supply the rest elements as function arguments,
recursively evaluating them in-place.
Let's write various functions to extend this basic interpreter.

quote
.....

Quoting is used to separate expressions from data in Lisp.
For example, in Emacs-Lisp it is ``(quote 1 2 3)``, which is usually
written via quotation prefix as ``'(1 2 3)``. Without quotation,
Lisp will interprete this as a function call, where the first symbol
(``1``) is a function name and ``2 3`` - are function arguments.
Because we are limited by Python syntax, it is impossible to introduce
Lisp-alike special quote forms, i.e. ``'(1 2 3)``. Thus, ``quote``
should be written as a function:

.. code-block:: python

  def quote(*args):
      """Returns a list without evaluating it."""
      return tuple(args)

  eval((quote, 'x', 3, 0.7))
  >>> ('x', 3, 0.7)

**Please be aware**, that this is still a rudimentary quotation, which
does not work correctly for quoted sub-lists. For example, in any
Lisp the following evaluation takes places:

.. code-block:: lisp

  '(1 2 '(3 4))
  >>> (1 2 (quote 3 4))

However it evaluates to the following code in this mini-interpreter:

.. code-block:: python

  (1, 2, (3, 4))


plus
....

Let's write a mathematical function. Usually the ``+`` operator is used
in various Lisp dialects for summing, but we are still limited with
Python's syntax, which would not allow writing ``(+, 2, 3)``.

.. code-block:: python

  def plus(*args):
      """Sums up the input arguments."""
      return sum(args)

  eval((plus, 3, 4, 5))
  >>> 12

And here come two nice examples with recursion:

.. code-block:: python

  eval((plus, 3, 4, (plus, 5, 6)))
  >>> 18

  eval((plus, (plus, 3, 4), (plus, 5, 6)))
  >>> 18


apply
.....

What happens if you try to plus a list, like ``(plus, (quote, 1, 2, 3))``?
The interpreter will crash because it will end up calling Python's
``sum`` as ``sum([(1, 2, 3), ])``. A typical Lisp dialect deals with this
problem via ``apply`` function:

.. code-block:: python

  def apply(*args):
      """Applies a function to a list of arguments."""
      fn = args[0]
      fn_args = args[1]
      return fn(*fn_args)

  eval((apply, plus, (quote, 1, 2, 3)))
  >>> 6


map and inc
...........

The ``map`` function takes another function and a list as input, applies
the function to each element of this list and returns the results in a new
list. For example: ``(map, inc, (quote, 1, 2, 3))`` returns ``(2, 3, 4)``.

Here, ``inc`` - is a simple function which returns the value of it's
argument + 1. For example, ``(inc, 10)`` returns ``11``.


.. code-block:: python

  def map(*args):
      """Apply the function to each element of the list and return
         the results in a new list."""
      fn = args[0]
      fn_args = args[1]
      return tuple(fn(item) for item in fn_args)

  def inc(arg):
      """Increases the argument by 1."""
      return arg + 1

  eval((map, inc, (quote, 1, 2, 3)))
  >> (2, 3, 4)


lambdas
.......

I was looking for a nice way of writing lambdas without modifying
the base interpreter. Unfortunately using the Python lambdas directly
would require putting an explicit ``eval()`` in the lambda body, e.g.:

.. code-block:: python

  eval((map, lambda x: (plus, x, 1), (quote, 1, 2, 3)))

Would not work because ``(plus, x, 1)`` is never evaluated. To make
this work we have to write it as:

.. code-block:: python

  eval((map, lambda x: eval(plus, x, 1), (quote, 1, 2, 3)))

which destroys the consistency of the syntax. Ruby code blocks would
be indeed helpful here :)

I will stop extending the interpreter now. As you see the interpreter
is not complete and it is quite primitive. But the aim of this article
is to show another way of demonstrating and teaching recursion in Python
through the beauty of Lisp :) I hope you enjoyed it!
Looking forward for your comments and solutions!
