Is it a string?
===============

:slug: is_it_a_js_string
:categories: Articles
:tags: JavaScript, programming
:date: 2013-09-23 12:00

:summary: How do you know if a Javascript variable is actually a string? There are several ways to answer this simple question.

The most straightforward method of getting a variable type in javascript is
using the ``typeof`` operator:

.. code-block:: js

  typeof 'abc'
  >> "string"

In a simple case

.. code-block:: js

  s = 'abc'
  typeof(s) == 'string'

But what do we know about javascript strings?

  The String global object is a constructor for strings, or a sequence of characters.
  String literals take the forms [1]_:

.. code-block:: js

    'string text'
    "string text"

  Or, using the ``String`` global object directly:

.. code-block:: js

    String(thing)
    new String(thing)

Now that is where it becomes a bit tricky:

.. code-block:: js

  s = String('abc')
  >> 'abc'
  typeof s
  >> 'string'
  so = new String('abc')
  >> { '0': 'a',
       '1': 'b',
       '2': 'c' }
  typeof so
  >> 'object'  // it is not a 'string' anymore!


And there is nothing wrong with the latter statement as because first of all ``so`` is ``Object``
created via the ``new`` operator. Fortunately the ``instanceof`` operator can handle this scenario:

.. code-block:: js

  so instanceof String
  >> true

.. [:ref:`skip to the code <thecode>`]
.. _thecode:

The code
--------

.. code-block:: js

  isString = function(s) {
    return typeof(s) == 'string' || s instanceof(String);
  }

  isString('abc')
  >> true
  isString(new String('abc'))
  >> true
  isString(321)
  >> false

References
----------

.. [1] `Mozilla Developer Network: String <https://developer.mozilla.org/en-US/docs/JavaScript/Reference/Global_Objects/String>`_
