Python nightmares: Implicit `this`
==================================

:slug: python_nightmares_implicit_this
:categories: Articles
:tags: Python, programming
:date: 2015-05-11 22:00


:summary: I met a lot of Python beginners who complained about ``this``
  keyword not implicitly available in class methods. After all,
  why pass ``self`` explicitly?

My first line of defense against such heresy is
`PEP 20 - The Zen of Python <https://www.python.org/dev/peps/pep-0020/>`_,
which states that *Explicit is better than implicit.*
Next comes the fact that Python class methods are in functions, bound
to a class instance via descriptor protocol.
If this sounds complex, I strongly encourage you to check the great
`Descriptor HowTo Guide <https://docs.python.org/3/howto/descriptor.html>`_
from the official documentation.
In general, passing function arguments through magic variables is awful
(think of Perl with its ``$``)!
Why pass an object through a magical ``this``?

Finally, it is possible to hide ``self`` and pass ``this`` implicitly.
The easiest way is to do it by decorating a method:

.. code-block:: python

  # NOTE: all code examples are done in Python 3

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

Output:

.. code-block:: pycon

   Alex says: Can you believe it? There is no `self` here!

As you can see, there is no ``self`` argument in ``say()`` method,
but there is an implicit ``this``! What happens in ``add_this()``
decorator is that we modify function's ``__globals__`` dictionary,
adding ``this`` variable with value of ``self`` to the scope.
Recall that ``__globals__`` is

  A reference to the dictionary that holds the function’s
  global variables — the global namespace of the module in
  which the function was defined [1]_.

Thus, modifying it, we also modify the global scope of the current
module. This is certainly not the way to go, but is enough for
simple demonstration.

If that is not crazy enough, let's write a metaclass which takes
care of decorating methods automatically:

.. code-block:: python

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

Output:

.. code-block:: pycon

  Daniel says: And now, there is only AddThisMeta!
  Daniel runs away :)

Here, the metaclass does the same job we did above: it wraps
all the methods which have a plain ``function`` type in class dictionary
via ``add_this()`` decorator.

As you can see, it is not hard at all to introduce an implicit ``this``
in your code. But please, for all the good we have in Python,
**don't even think about doing it!**.

References
**********

.. [1] https://docs.python.org/3/reference/datamodel.html
