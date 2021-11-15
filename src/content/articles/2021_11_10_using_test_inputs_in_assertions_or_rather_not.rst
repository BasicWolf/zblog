Using tests inputs in assertions (or rather not)
################################################

:slug: using_tests_inputs_in_assertions_or_rather_not
:categories: Articles
:tags: programming, python, testing, unit tests
:date: 2021-11-10 12:00
:summary:
   .. image:: {static}/images/articles/2021_11_10_using_test_inputs_in_assertions_or_rather_not/cover_straight_knot.jpg
      :width: 70%
      :align: center
      :alt: beautiful [but deadly] square knot / by woodleywonderworks / https://www.flickr.com/photos/wwworks/5623339500 / License: Attribution 2.0 Generic (CC BY 2.0)

   It might be very convenient to use the same fixtures in test
   setup and assertions. This practice though is not as good as it looks
   like at first glance.

.. image:: {static}/images/articles/2021_11_10_using_test_inputs_in_assertions_or_rather_not/cover_straight_knot.jpg
   :width: 70%
   :align: center
   :alt: beautiful [but deadly] square knot / by woodleywonderworks / https://www.flickr.com/photos/wwworks/5623339500 / License: Attribution 2.0 Generic (CC BY 2.0)

Imagine that we have to implement a *adding a title to a document*.
The relationship between ``Title`` and ``Document`` is straightforward
and we begin by writing a test:

.. code-block:: python3

   def test_add_title_to_document():
       document = Document()
       title = Title("Lorem Ipsum")

       document.add_title(title)

       assert document.title == title

Take a minute to spot the weak points of the code above and let's discuss them.

Test-First Loop
===============

People who practice test-driven development sometimes focus on the details of
the process too much.
We start by writing a test. Sometimes we write it to the end, sometimes we
add small portions. The test fails and we write implementation to fix the failing
part.
The cycles repeats until the test is fully written and the implementation
fulfills the test. The satisfied developer moves to the next task, everyone
is happy.
Is there something missing though?

The Ultimate Test
=================

If someone asks you, what was the ultimate purpose of any test
(we're speaking of software development of course) what would you answer?

I think that the goal of any test is to **confirm the relationship
between certain inputs and outputs of a routine**. The routine size doesn't matter
- it could be as small as a function in a unit test or as big as a complex behavior
of multiple services in an end-to-end test.

This brings us back to the code above. The input is ``Title("lorem ipsum")``.
What about the output?


Outputs ≠ Inputs
================

The output of the test above is also the input. That is the biggest evil
here. There is absolutely no way to fail this test by modifying the input:

.. code-block:: python3

   def test_add_title_to_document():
       document = Document()
       title = Title("dolor sit amet")  # changes don't affect test behaviour

       document.add_title(title)

       assert document.title == title


However, the test fails if input and output are separated:

.. code-block:: python3

   def test_add_title_to_document():
       document = Document()
       title = Title("dolor sit amet")
       document.add_title(title)

       assert document.title == Title("Lorem Ipsum")  # hooray, this fails!


Test-First Loop: Extended edition
=================================

My colleague `Jere Teittinen <https://jereteittinen.info>`_
taught me an amazingly simple and useful trick about writing tests.
When you are done with the test and the routine behind it, **change the
inputs or outputs to verify that the test fails**. This is an important
step which **protects from tailored routine implementation**.
Such routine is able to fulfill the test only with the original inputs
and outputs. You shake them a bit and everything falls apart like
a house of cards.
