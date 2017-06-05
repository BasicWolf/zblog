C's heritage: bitwise and equality operators
============================================

:slug: cs_heritage_bitwise_and_equality_operators
:categories: Articles
:tags: programming, C, JavaScript
:date: 2011-12-29 12:00

:summary: The design of C made by Brian Kernighan and Dennis Ritchie has influenced the whole software and hardware industry. Sometimes you can feel the heritage of C even in modern high-level dynamic languages like Javascript.

I've stumbled in a Javascript situation where bitwise operators were used.
Logically, a bitwise operator should have a higher precedence than an
equality operator, e.g:

.. code-block:: js

  if x | 10 == y
      alert("We've got it!")

But it looks like that this code would work the other way, as in JavaScript
bitwise operators have lower precedence than equality operators do (see
Mozilla's JS reference). The code above would always return 0 for any valid
numerical val, because the result of val & true is 0. So, the proper way
would be to put parenthesis around bitwise expression:

.. code-block:: js

  if (x | 10) == y
     alert("We've got it!")

I dug up the history of the question and it seems like this behaviour
comes from the age of K&R's C:

.. epigraph::

   Early C had no separate operators for & and && or | and ||. (Got that?)
   Instead it used the notion (inherited from B and BCPL) of "truth-value
   context": where a Boolean value was expected, after "if" and "while"
   and so forth, the & and | operators were interpreted as && and || are
   now; in ordinary expressions, the bitwise interpretations were used.
   It worked out pretty well, but was hard to explain. (There was the notion
   of "top-level operators" in a truth-value context.)

   The precedence of & and | were as they are now.
   ...

   In retrospect it would have been better to go ahead and change the
   precedence of & to higher than ==, but it seemed safer just to split
   & and && without moving & past an existing operator. (After all, we
   had several hundred kilobytes of source code, and maybe 3
   installations....)

   -- Dennis Ritchie [1]_.

In terms of logical statement in C:

.. code-block:: c

  if (x == 1 & y == 0) {
      /* ... */
  }

Makes perfect sense. But it doesn't make any in terms of bitwise logic.

C++, Java, Objective-C, PHP, C# and finally Javascript have it the same
way. Python, Ruby, Go have it the other way around.

Do you know any reasons (apart from the one that comes from C's heritage)
which made programming languages' designers to follow C's precedence rules?


References
----------

.. [1] http://www.lysator.liu.se/c/dmr-on-or.html
