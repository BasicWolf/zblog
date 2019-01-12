The ultimate guide to Python decorators
#######################################

:slug: the_ultimate_guide_to_python_decorators
:categories: Articles
:tags: Python, programming
:date: 2017-01-22 23:00

:summary: Decorators are one of the most beautiful feature of Python
          programming language. They can make code easy-readable
          and maintainable. Nevertheless, their usage may seem tricky
          and mysterious in the beginning.
          This is a guide to the world of decorators. I hope that
          you will feel like a pro and have no questions left about them
          after exploring this article.


.. contents::
   :backlinks: none
   :depth: 2


Introduction to decorators
==========================

Historical background
---------------------

It all started with discussion on how-to turn the following syntax
into something nice:

.. code-block:: python3

   class C(object):
       def info():
           return 'This is class C'

       info = staticmethod(info)

This is an absolutely valid code, however declaring ``info`` as a
static method requires wrapping it as ``info = staticmethod(info)``.
Inconvenient, isn't it?

In case you are not familiar with ``staticmethod()`` [1]_: it is a builtin
function which accepts a function as an argument and creates a static method for the class.
This is all done via `descriptors protocol <https://docs.python.org/3/howto/descriptor.html>`_,
but no need to go that deep today. At this point, ``info()`` can be called as

.. code-block:: pycon

   >>> C.info()
   This is class C

After months of discussion, analysis and research
`PEP 318 -- Decorators for Functions and Methods <https://www.python.org/dev/peps/pep-0318/>`_
was finally accepted. Since Python 2.4 decorators turned the code above into

.. code-block:: python3

   class C(object):

      @staticmethod  # this is a decorator
      def info():
          return 'This is class C'


.. _what-decorators-are:

Geting to know decorators
-------------------------

A decorator is a syntactic sugar of calling a function which
accepts another function as an argument and returns either the
same function or another callable. *Note: this
definition is not complete and will be expanded further in the
article*.

Take a look at these nice decorators examples:

.. code-block:: python3

  # Django web framework view decorators
  @login_required
  @require_GET
  def my_view(request):
      # I can assume now that only GET requests
      # from a logged in user make it this far.
      # ...


  # Flask web microframework routing
  @app.route("/")
  def hello():
      return "Hello World!"


  # Standard library unit tests
  class MyTestCase(TestCase):

      @skipUnless(sys.platform.startswith("win"), "requires Windows")
      def test_windows_support(self):
          # windows specific testing code
          # ...


No doubt, decorators improve the readability of code dramatically.


.. _closures:

Closures
--------

Let's take a look at a practical example to see how decorators work from
the inside. Imagine that you want to log all the
arguments' values and the return value of a
``send_message(sender, receiver, text='')`` function calls to ``stdout``.
This can be simply done via ``print()`` as follows:

.. code-block:: python3

   def send_message(sender, receiver, text=''):
       print('send_message was called')
       print('The arguments are sender={}, receiver={}, text={}'
             .format(sender, receiver, text))
       ...
       print('The return value is "SENT"')
       return 'SENT'

However, consider that you now have to do the same for dozen other
functions, all with different arguments and return values.
First, let's do this without decorators:

.. code-block:: python3

   def send_message(sender, receiver, text=''):
       ...

   def send_message_with_log(*args, **kwargs):
       ret = send_message(*args, **kwargs)
       print('send_message was called')
       return ret

   # Important substitution
   send_message = send_message_with_log

To make ``send_message_with_log`` more generic, a technique called
`closure <https://en.wikipedia.org/wiki/Closure_(computer_programming)>`_
is used as follows:

.. code-block:: python3

   def send_message(sender, receiver, text=''):
       ...

   def log_fn(f):
       def wrapper(*args, **kwargs):
           ret = f(*args, **kwargs)
           print('{} was called'.format(f.__name__))
           return ret
       return wrapper

   send_message_with_log = log_fn(send_message)
   send_message = send_message_with_log

Here, value of ``f`` is stored in lexical scope of ``wrapper``, which means
that after ``send_message_with_log = log_fn(send_message)``, ``send_message_with_log`` variable
has a value of the ``wrapper`` function with ``send_message`` stored in
``f`` variable. Finally, the *original* ``send_message`` is substituted.
In a single line:

.. code-block:: python3

   send_message = log_fn(send_message)


Calling ``send_message`` will produce the following output:

.. code-block:: pycon

   >>> send_message()
   send_message was called

Note, that ``log_fn`` is now generic and can be used to log any functions' calls.


.. _your_first_decorator:

Your first decorator
--------------------

Now we are ready to turn ``log_fn`` into a decorator.
Let's write it down and analyze its code line-by-line:

.. code-block:: python3

   def log_fn(f):
       def wrapper(*args, **kwargs):
           ret = f(*args, **kwargs)
           print('{} was called'.format(f.__name__))
           ...
           return ret
       return wrapper

   @log_fn
   def send_message(sender, receiver, text=''):
       ...
       return 'SENT'

``1. def log_fn(f):`` - a decorator is defined. It is a function
which accepts a single argument - another function.

``2. def wrapper(*args, **kwargs):`` - an internal function (a closure technique)
which wraps calls to function ``f`` with custom logic. For a moment let's
skip the body of ``wrapper()`` and proceed to the end of ``log_fn()``.

``7. return wrapper`` - the return value of the decorator. It returns
a callable, which is usually an internal wrapper function.

``9. @log_fn`` - at this point decorator is called with
``send_message`` as an argument. This is equivalent to:

.. code-block:: python3

   def send_message(sender, receiver, text=''):
       ...

   # send_message is substituted
   send_message = log_fn(send_message)

Pay attention to the ``wrapper`` function, which is returned
by ``log_fn()`` and assigned to ``send_message``. What happens
to the original ``send_message``? Let's get back to the body of
``wrapper``.

``3. ret = f(*args, **kwargs)`` - here the original ``f`` function
is called. At this point, ``f == send_message``.

``4. print('{} was called'.format(f.__name__))`` - a simple logging
to stdout, which prints ``"send_message was called"`` each time the
function is called

``5. return ret`` - the return value of the original function
call is returned

Finally, let's update the decorator to make it more useful and fulfill
the original requirements of logging the function call with the
arguments and the return value:

.. code-block:: python3

   def log_fn(f):
       def wrapper(*args, **kwargs):
           ret = f(*args, **kwargs)
           sargs = ', '.join(repr(arg) for arg in args)
           skwargs = ', '.join('{}={}'.format(k, repr(v))
                               for k, v in kwargs.items())

           print('{name}( {sargs}, {skwargs} ) => {ret}'.format(
                 name=f.__name__,
                 sargs=sargs,
                 skwargs=skwargs,
                 ret=repr(ret)
           ))
           return ret
       return wrapper

So, the output of calling the decorated ``send_message`` is:

.. code-block:: pycon

   >>> send_message('alice', 'bob', text='Hello!')
   send_message( 'alice', 'bob', text='Hello!' ) => SENT




Examples
--------

Decorator syntax allows quick and clear extension of the wrapped
functions. Its beauty is in simplicity: by writing a single line declaration
one can embed powerful functionality while keeping the code clean and neat.

Let's explore decorators possibilities by writing a couple of
decorators which might be handy in development.

debug_on_error
..............

.. code-block:: python3

   import pdb;

   def debug_on_error(f):
       """Drop to pdb debugger on exception"""
       def wrapper(*args, **kwargs):
           try:
               return f(*args, **kwargs)
           except Exception as e:
               pdb.post_mortem()
       return wrapper

   # usage
   @debug_on_error
   def div(x, y):
       return x / y

This decorator allows dropping into debugger the moment an error
occurs in a function call. For example running the following code
in ipython3:

.. code-block:: pycon

   >>> div(5, 0)
   <ipython-input-2-cd786e30d343>(3)div()
   -> return x / y
   (Pdb) ?


timeit
......

.. code-block:: python3

   import time

   def timeit(f):
       """Measure an execution time of the wrapped function"""
       def wrapper(*args, **kw):
           tick = time.time()
           ret = f(*args, **kw)
           tock = time.time()

           print('{}() execution time: {} s.'.format(f.__name__, tock - tick))
           return ret

       return wrapper

   # example
   @timeit
   def sum_up_to(x):
       res = 0
       for i in range(0, x):
           res += i
       return res

This decorator prints the amount of seconds passed between function
call and return events. It is helpful to measure a function's execution
time and find performance bottlenecks. Let's run an example:

.. code-block:: pycon

   >>> sum_up_to(int(10e6))
   sum_up_to() execution time: 0.0465855598449707 s.


.. _chaining-decorators:

Chaining decorators
-------------------

Imagine that you want to log the function call with ``log_fn`` and
at the same time profile it with ``timeit`` decorators.
Just chain the decorators! For example:

.. code-block:: python3

  @timeit
  @log_fn
  def sum_up_to(x):
      ...

This is the same as:

.. code-block:: python3

  def sum_up_to(x):
      ...

  sum_up_to = timeit(log_fn(sum_up_to))

There are virtually no limits on the amount of decorators decorating
a function (beside the stack limit) however you may want to keep that
number low for code readability.


.. _decorators-with-arguments:

Decorators with arguments
=========================

So far we've been exploring simple decorators and their usage,
which is just the tip of the iceberg. For example, decorators
accept arguments the same way as any ordinary function does.
This makes them even more powerful and versatile.
But before jumping there, let's take a look at an important
technique which always follows decorators source.

.. _wrapping-functions-properly:

Wrapping functions properly
---------------------------

Let's call ``sum_up_to()`` from the last example, where it
has been decorated with both ``timeit`` and ``log_fn``.
The printed result may look a little bit unexpected:

.. code-block:: pycon

  >>> sum_up_to(int(10e6))
  sum_up_to( 10000000,  ) => 49999995000000
  wrapper() execution time: 0.4475877285003662 s.

Did you notice that the name of the function in the output
is not ``sum_up_to`` but ``wrapper``? This behaviour is not a bug.
Take a minute to find out why this happens.

Let's unwrap the decorator call:

.. code-block:: python3

  # Python unwraps the decorator call into this:
  sum_up_to = timeit(log_fn(sum_up_to))

  # First, log_fn(sum_up_to) is executed, which returns
  # log_fn's internal `wrapper` function:
  log_fn_wrapper = log_fn(sum_up_to)

  # Hence, `timeit` is called with `log_argument_wrapper`
  # as an argument:
  sum_up_to = timeit(log_fn_wrapper)

The problem is that ``wrapper`` does not mimic the original function. To overcome this, attributes like ``__name__``, ``__doc__``, ``__module__`` etc. from the original function should be copied to ``wrapper``:

.. code-block:: python3

  def timeit(f):
      def wrapper(*args, **kw):
          ...

      wrapper.__name__ = f.__name__
      wrapper.__doc__ = f.__doc__
      wrapper.__module__ = f.__module__
      return wrapper

Though this code works fine, it means that one would have to write the same attributes copying routine in every decorator. Sounds familiar? Indeed, why not write yet another decorator, which does the attributes copying? Guess what, the standard library already contains a function ``wraps()`` [2]_ which gracefully handles this issue:



.. code-block:: python3

  from functools import wraps

  def timeit(f):
      @wraps(f)
      def wrapper(*args, **kw):
         ...
      return wrapper

  def log_fn(f):
      @wraps(f)
      def wrapper(*args, **kwargs):
          ...
      return wrapper

  @timeit
  @log_fn
  def sum_up_to(x):
      ...

  >>> sum_up_to(int(10e6))
  sum_up_to( 10000000,  ) => 49999995000000
  sum_up_to() execution time: 0.9093782901763916 s.


Wonderful! Now ``timeit()`` prints the name of the decorated function.
One thing you have probably noticed about ``wraps`` is that it actually accepts an argument! Now that you know how-to wrap a decorator properly, let's find out how to pass arguments to decorators.


.. _decorators-and-arguments:

Decorators and arguments
------------------------

Decorators are functions, so they accept arguments the same way as any other function does.
For example, let's update the ``timeit`` decorator to log the function calls
which take more than N seconds to complete:

.. code-block:: python3

   @timeit(0.1) # 100 milliseconds
   def sum_up_to(x):
       ...

How to implement such a decorator? Remember that by definition,
a decorator accepts a single argument only (i.e. the decorated function),
thus accepting an integer in the example above breaks the rules.
The trick is that it is not ``timeit`` which decorates ``sum_up_to``,
but rather the result of ``timeit(0.1)`` call:


.. code-block:: python3

   def timeit(limit):
       def decorator(f):
           @wraps(f) # wrap properly
           def wrapper(*args, **kw):
               ...
           return wrapper
       return decorator


What happens when a function e.g. ``sum_up_to`` is decorated as ``@timeit(0.1)``?
First, Python calls ``timeit(0.1)`` which **builds** a decorator and returns it.
Then, Python decorates ``sum_up_to`` with the obtained decorator. It all can be
decomposed as follows:


.. code-block:: python3

  def timeit(limit):
      ...
      return decorator

  timeit_decorator_100ms = timeit(0.1)

  @timeit_decorator_100ms
  def sum_up_to(x):
      ...


There are no limits on decorators' arguments design. For example, a
version of ``timeit`` which accepts two arguments: a limit and a printer
function:


.. code-block:: python3

   import logging
   log = logging.getLogger(__name__)

   def timeit(limit, printer_fn=print):
       def decorator(f):
           @wraps(f)
           def wrapper(*args, **kw):
               ...
               if diff > limit:
                   printer_fn('{}() execution time: {:.2} s.'.format(f.__name__, diff))
               return ret
           return wrapper
       return decorator

   @timeit(100, printer_fn=log.warning)
   def sum_up_to(x):
       ...


Class as a decorator
--------------------

Python allows taking the idea of decorators with arguments even further.
Classes can be effectively used to reduce the amount of nested functions
and to improve the code of  complex decorators.

There is no magic in using classes: first, Python creates an object
from a class and then calls it (i.e. invokes object's ``__call__()`` method)
to decorate a function.

Let's rewrite ``timeit(limit, printer_fn)`` as a class. The arguments are
passed through ``__init__()`` method and are stored as class attributes.
The ``__call__()`` method returns a wrapped function:

.. code-block:: python3

   class timeit:
       def __init__(self, limit, printer_fn=print):
           self.limit = limit
           self.printer_fn = printer_fn

       def __call__(self, f):
           @wraps(f)
           def wrapper(*args, **kw):
               tick = time.time()
               ret = f(*args, **kw)
               tock = time.time()
               diff = tock - tick
               if diff > self.limit:
                   self.printer_fn('{}() execution time: {:.2} s.'.format(f.__name__, diff))
               return ret
           return wrapper

   @timeit(0.01)
   def sum_up_to(x):
       res = 0
       for i in range(0, x):
           res += i
       return res


     sum_up_to(int(10e6))
     >>> sum_up_to() execution time: 1.0 s.


.. _function-vs-class:

Function-decorators vs. class-decorators
----------------------------------------

`PEP-20 <http://python.org/dev/peps/pep-0020/>`_ states that

..

  There should be one-- and preferably only one --obvious way to do it.
  Although that way may not be obvious at first unless you're Dutch.

Unless writing decorators on a regular basis, one would wonder, what
are the benefits of using function-decorators vs. class-decorators and vice-verse?
Function-decorators are

* Simple and clear when no decorator arguments are required.
* Even simpler when a decorator returns the original function, not a wrapper.

However class decorators

* Allow better decomposition of complex decorators.
* Provide clearer syntax to store **state** of a decorator both local and global.

The choice whether to write a decorator as a function or a class always depends
on the case or personal preferences. As a rule of thumb -
if the logic behind the decorator is complex, then go on with a class.
Otherwise, pick a function approach.


.. _decorating-methods:

Decorating methods
==================

The syntax of decorating class methods is similar to decorating functions:

.. code-block:: python3

  class Calculator:

      @log_fn
      @timeit
      def sum(self, x, y):
          ...

You are most probably familiar with the built-in ``property`` [6]_, ``classmethod`` [7]_ and ``staticmethod`` [1]_
decorators. For example here a calculator's epsilon is a read-only property:

.. code-block:: python3

  class Calculator:
      _eps = 0.00001

      @property
      def eps(self):
          return self._eps

  calc = Calculator()
  print(calc.eps)
  >>> 0.00001

  calc.eps = 0.0001
  >>> Traceback (most recent call last):
  >>> File "<stdin>", line 1, in <module>
  >>> AttributeError: can't set attribute


Self and method decorators
--------------------------

Method decorators may have an explicit access to self. Consider this:

.. code-block:: python3

   def decorator(m):
       # WARNING, do not do this!
       def wrapper(self, *args, **kwargs):
           return m(self, *args, **kwargs)
       return wrapper

However this is a dangerous construction. A generic decorator **should not** access ``self``
argument of the decorator method. As a matter of fact, a generic decorator **should not** know
anything about the decorated callable, whether it is a function, a method, or a
wrapper returned by another decorator. Otherwise it breaks the universal protocol
and for example makes impossible chaining the decorators in an arbitrary order.



.. _decorating-classes:

Decorating classes
==================

When function decorators were originally debated for inclusion in Python 2.4, class decorators were seen as obscure and unnecessary thanks to metaclasses. After several years' experience with the Python 2.4.x series of releases and an increasing familiarity with function decorators and their uses, Guido van Rossum aka BDFL and the community re-evaluated class decorators and recommended their inclusion in Python 3.0 [3]_.

The use cases however are not that obvious [4]_. That is because
which could be done via class decorators, could be as well done
via good old metaclasses. It seems that *the* usage case is
registering a class in any kind of chain like a plugins
system.

A hint of such usage, is the standard library's ``unittest.skip*`` [5]_ functions,
for example:

.. code-block:: python3


    @unittest.skipUnless(settings.LOGGING_ENABLED):
    class LoggingTest:
        def test_smoke(self):
            ...

This test will be executed, only if a `Logging` feature is enabled
in application's settings.

Consider another example: a media player application which supports plugins:

.. code-block:: python3

   from player.plugins import Plugin, register


   class AACPlugin(Plugin):
       ...

   register(AACPlugin)

   # This plugin is still experimental and is not
   # registered in Player's plugins system
   class AACExperimentalPlugin(Plugin):
       ...


Wouldn't it be easier to write

.. code-block:: python3

   @register
   class AACPlugin(Plugin):
       ...

?

Also, why not automatically register the plugins which inherit from ``Plugin``
class? Gotcha! What if you **do not** want to register the plugin yet, whether
it is experimental, or incomplete, or for any other reason? That's where
decorators allow expressing developer's intention in a clear and non-ambiguous
manner.


Example: Registering a plugin
-----------------------------

Let's consider the case described above : A media player application has a plugins system
which extend its basic capabilities. A ``player.plugins.register()`` call is used
to register an arbitrary class as a plugin. An API user should not care, about
``register()`` 's internals, however in this case, ``register()`` simply validates
the classes and stores them in a global ``_plugins`` list:

.. code-block:: python3

   # --- in player/plugins.py --- #

   _plugins = []

   class Plugin:
       '''Plugin base class'''


   def register(cls):
       if not isinstance(cls, Plugin):
           raise TypeError('Cannot register a class as a Plugin: wrong type {}'.format(type(cls)))

       _plugins.append(cls)

       return cls


  # --- usage in 3d-party module --- #

  from player.plugins import Plugin, register

  @register
  class AACPlugin(Plugin):
      ...

Finale
======

This is it! Thank you for reading, I hope you enjoyed!
Please leave a comment, ask a question, or just share this article with
anyone who is still lost in the world of Python decorators :)


References
==========


.. [1] `staticmethod <https://docs.python.org/3/library/functions.html?highlight=staticmethod#staticmethod>`_
.. [2] `@functools.wraps <https://docs.python.org/3/library/functools.html?highlight=wraps#functools.wraps>`_
.. [3] `PEP 3129 <https://www.python.org/dev/peps/pep-3129/>`_
.. [4] `Class decorators in Python: practical use cases <http://softwareengineering.stackexchange.com/questions/334195/class-decorators-in-python-practical-use-cases>`_
.. [5] `unittest.skip <https://docs.python.org/2/library/unittest.html#unittest.skip>`_
.. [6] `property <https://docs.python.org/3/library/functions.html?#property>`_
.. [7] `classmethod <https://docs.python.org/3/library/functions.html?#classmethod>`_
