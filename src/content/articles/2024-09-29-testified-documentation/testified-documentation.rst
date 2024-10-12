.. role:: strike
    :class: strike

Testified Documentation
#######################

:slug: testified-documentation
:category: Articles
:tags: programming, python, documentation, tests, specification, BDD, collaboration, cucumber
:date: 2024-09-29 14:47
:status: published

:summary:
   It's hard to sell a software product - whether it's a library, a program,
   or generally speaking, a system - if it doesn't come with a top-notch manual.
   And keeping such manual up-to-date is not easy too.
   Gojko Adzic's ideas of `Living Documentation
   <{filename}../2023_02_21_specification_by_example/specification_by_example_book_review.rst>`_ to the rescue, but unfortunately they are still far from being widely adopted.

   In this post I propose a different way of making Living Documentation -
   by testifying its contents. Dive in to find out how!

   .. image:: {static}img/testified-documentation-horizontal.webp
      :target: {filename}testified-documentation.rst
      :align: center
      :alt: Testified documentation diagram

..


   The manual is outdated unless you are continuously
   building it alongside the application.

   -- `Arho Huttunen <https://www.arhohuttunen.com>`_

It's hard to sell a software product - whether it's a library, a program,
or generally speaking, a system - if it doesn't come with a top-notch manual.
In my opinion, a good manual should describe
every aspect of the system, provide plenty of different high-level examples
and lower-level API specifications. It includes a changelog with
emphasised important and breaking changes, explains how to install, upgrades
and maintain the system.

Keeping such documentation up-to-date is hard. Even when engineers who
work on the system take care of the manual, they easily miss some tricky aspects
or don't bother to document certain "obvious" behaviour.
It's even harder for technical writers who work in silos and don't know much
about the internals of the system, or don't fully understand the business case
covered by the product feature they are documenting.



Specification by Example and Cucumber
=====================================

Gojko Adzic proposed the concept of Living Documentation in his renowned book
`"Specification by Example" <{filename}../2023_02_21_specification_by_example/specification_by_example_book_review.rst>`_.
But Living Documentation doesn't come for free.
For a :strike:`JIRA ticket` a new feature description to become
an executable specification, one must first lay down a bridge between the human-friendly
narrative and the machine.

For example: A fictional Flixnet movie streaming platform wants to notify the
customers that their subscriptions are about to expire.
After user mapping sessions, the stakeholders wrote down the following
specification expressed in Gherkin/Cucumber syntax:

.. code-block:: gherkin

   Feature: Remind a customer about an expiring subscription

     The customer might forget that their Flixnet subscription is expiring.
     We want to retain the customer by reminding them about the expiring subscription
     and providing an easy way to remain subscribed.
     We will notify the customer only once, 3 days before the subscription expires,
     so that the customer is not annoyed.

     Scenario: An active customer whose subscription expires in 3 days gets a notification
       Given an active customer
       And their subscription expires in 3 days
       And we have not sent them a reminder yet
       Then send the customer a reminder

How do we organise the document that incorporates
this specification? Should it have a link to the specification? Or take
some of its parts, like the feature name and description? Remember that Gherkin
pays no attention to those, they are for the reader's convenience only.
With some effort, it is possible to program `docutils <https://docutils.sourceforge.io>`_
or `MyST <https://myst-parser.readthedocs.io/en/latest/>`_
directive to include the specification into a Markdown file:

.. code-block:: markdown

   ### User notifications and reminders

   We send our users notifications on certain occasions. They are listed below:

   ```{specification}
   :feature: Remind a customer about expiring subscription
   :include-description:
   ```

   ...

*Coupled with the ability to check specification execution (aka tests) results*,
this could provide a living documentation!
It's quite close, to what Gojko Adzic described
in his 10-years-later aftermath `article <https://gojko.net/2020/03/17/sbe-10-years.html>`_
written in 2020. He noticed, that with then-available breed of
Given-When-Then tools, the most effective solution was converting
the specification files into something nicer and easier to read
and then publishing a read-only version somewhere outside the version
control system.

The sad part is that specifications written in Gherkin and executed via Cucumber
are largely abused. Aslak Hellesøy wrote in 2014 that Cucumber was
`largely misunderstood
<https://cucumber.io/blog/collaboration/the-worlds-most-misunderstood-collaboration-tool/>`_.
Cucumber is first a formost a *collaboration tool* that aims to bring a
common understanding to software teams - across roles. It is not a testing tool
for QA to write end-to-end tests on an existing implementation.
I witnessed horrible Cucumber misuse: specifications written weeks after
implementation got integrated; Specifications which have only technical terms
and describe implementation details instead of business rules;
Specifications meaningless and repetitive, such as:

.. code-block:: cucumber

   Given a user
   When user logs in
   Then user is logged in

In other words, no one benefits from including *bad* Gherkin specification
details into a manual. And the tooling does not exist yet, anyway.


Testified Documentation
=======================

Back to square one - how else to ensure that the behaviour described in the
release manual aligns with the released program behaviour?

A simple idea struck me in September 2024.
What if we use something that is widely adopted by software engineers?
That is - the output of automated tests: unit, behaviour,
end-to-end - all of them that run on every build of the system.

.. image:: {static}img/testified-documentation.webp
   :target: {static}img/testified-documentation.svg
   :align: center
   :alt: Testified documentation diagram
   :width: 80%

Test automation tooling is widely available and is quite stable for popular
programming platforms.
Moreover, the test runners usually support a common
`JUnit XML <https://github.com/testmoapp/junitxml>`_ output format.
For example, here is the formatted report of two executed smoke tests:

.. code-block:: xml

   <?xml version="1.0" encoding="utf-8"?>
   <testsuites>
     <testsuite name="pytest" errors="0" failures="0" skipped="0" tests="2" time="0.041" timestamp="2024-09-29T14:19:49.292476+03:00" hostname="z">
       <testcase classname="test.test_smoke" name="test_smoke" time="0.001" />
       <testcase classname="test.test_smoke.TestBigSmoke" name="test_big_smoke" time="0.000" />
     </testsuite>
   </testsuites>

Now imagine that for every paragraph in documentation file, we could include a
directive that checks whether certain test cases successfully passed.

What if we also use artifacts produced by test automation in documentation?
For example, tests could make screenshots on certain steps,
and the documentation embeds them as example images.

I quickly assembled a small PoC for `Sphinx <https://www.sphinx-doc.org/en/master/>`_
- a tool widely used to write manuals for Python libraries and programs.
Here, I included a test name as a role
(yes, it should have been a directive ;-):

.. code-block:: rst

   This is a documentation for the "Spectest" library.

   Spectest starts with a simple smoke test. :spectest:`test.test_smoke.test_smoke`.

The build reads the test results from XML above, passes successfully and
outputs a Sphinx-based HTML manual.
However, if we simulate a test failure by changing the role to
``:spectest:`test.test_smoke.test_smoke1```, the build breaks along:

.. code-block:: none

   reading sources... [100%] index
   /home/zaur/projects/sphinx-spec-test/doc/source/index.rst:13: ERROR: TEST test.test_smoke.test_smoke1 not found [docutils]
   looking for now-outdated files... none found


That's the idea in a nutshell. To me it sounds *technically* simple enough to get
implemented for any extensible documentation generator.

The devil is however, in the details.
Testified documentation won't work well unless you have behavior tests.
That doesn't imply E2E tests at all! (I always profess keeping those to bare minimum)
Rather have a suite of fast `sociable tests <https://martinfowler.com/bliki/UnitTest.html>`_
that verify system behaviour and utilize stubs and mocks for external dependencies.

Feedback
========

Rainbows and unicorns :) I would love to hear your thoughts on this topic
and include them here. I am a lucky guy who can share the
wildest ideas with my colleagues and friends and get honest feedback.

`Jarkko 'jmp' Piiroinen <https://github.com/jmp>`_ had a very
valid and cool-minded point: there is zero incentive to make this kind of
documentation-to-test-results bindings if the target audience doesn't care
about full-fledged product documentation in the first place.

Seems to be the case, when a system is small enough to fit into
product team members heads,
and especially when the external interfaces are already documented
in a form of specification, like OpenAPI spec.
