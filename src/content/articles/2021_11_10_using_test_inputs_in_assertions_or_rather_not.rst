Using tests inputs in assertions (or rather not)
################################################

:slug: using_tests_inputs_in_assertions_or_rather_not
:categories: Articles
:tags: programming, python, testing, unit tests
:date: 2021-11-10 12:00
:summary: It might be very convenient to use the same fixtures in test
          setup and assertions. This practice though is not as good as it looks
          like at first glance.
:status: draft

Consider the function below, which tests adding a title to a document.

.. code-block:: python3

   def test_add_title_to_document():
       document = EmptyDocument()
       title = Title("Lorem Ipsum")

       document.add_title(title)

       assert document.title == title

Take a minute to spot the weak points of this code above and let's discuss them.

Test-First Loop
===============

People practicing test-driven development sometimes focus on details of
the process and forget what are the test supposed to do. [purpose]
You start by writing a small portion
of test, make it fail and write implementation to fix the failing part.
The cycles repeats until the test is fully written and the implementation
fulfills the test. The satisfied developer moves to the next task, everyone
is happy.
There is something missing though, isn't it?

The Ultimate Test
=================

If someone asks you, what was the ultimate purpose of any test
(we're speaking of software development of course) what would you answer?

I think that the goal of any test is to **confirm the relationship
between certain inputs and outputs of a routine**. The routine size doesn't matter
- it could be as small as a function in a unit test or as big as a complex behavior
of multiple services in an end-to-end test.

This brings us back to the code above. The input is clearly defined,
it is ``Title("lorem ipsum")``. What about the output?


Outputs ≠ Inputs
================

The output of the test above is also the input. That is the biggest evil
here. There is absolutely no way to fail this test by modifying the input:

.. code-block:: python3

   def test_add_title_to_document():
       document = EmptyDocument()
       title = Title("dolor sit ametm")  # changes don't affect test behaviour

       document.add_title(title)

       assert document.title == title


However, the test fails if inputs and outputs are separated:

.. code-block:: python3

   def test_add_title_to_document():
       document = EmptyDocument()
       title = Title("dolor sit amet")
       document.add_title(title)

       assert document.title == Title("Lorem Ipsum")  # hooray, this fails!


Test-First Loop: Extended edition
=================================

My colleague `Jere Teittinen <https://jereteittinen.info>`_
taught me an amazing trick.
When you are done with the test and the routine behind it, **change the
inputs or outputs to verify that the test fails**. This is an important
step which protects you from tailored routine implementation.
Such routine is able to fulfill the test only with the original inputs
and outputs. You shake them a bit and everything falls apart like
a house of cards.
