Refactoring - book review
#########################

:slug: refactoring_book_review
:category: Books
:tags: book, review, programming, refactoring, Martin Fowler, Kent Beck
:date: 2022-10-15 12:00
:summary:
   .. image:: {static}refactoring_book_cover_smallest.jpg
      :align: center
      :alt: "Refactoring" book front cover

   *Refactoring* is a book by Martin Fowler
   about what a fellow developer  might describe as
   "a process of improving the code quality."

   I highly recommend this book to software professionals who want to improve and formalise their refactoring skills.


.. image:: {filename}refactoring_book_cover_small.jpg
   :align: center
   :alt: "Refactoring" book front cover
   :width: 50%

*Refactoring* is a book by Martin Fowler (with contributions by Kent Beck)
about what a fellow developer  might describe as
"a process of improving the code quality."

Martin Fowler defines its meaning  more accurately:

..

  **Refactoring** (*noun*) -
  A change made to the internal structure of software to make it easier
  to understand and cheaper to modify without changing its observable behavior.

  **Refactoring** (*verb*) -
  To restructure software by applying a series of refactorings
  without changing its observable behavior.

So often developers refactor code and apply dozens of refactorings unconsciously!
We won't name the *small steps*, and don't categorise our actions - we merely
crave clean code.
Often we forget that the code should roughly do the same things it did before,
i.e. **the observable behaviour should not change**.

In a nutshell, "Refactoring" teaches detecting a piece of code that needs refactoring,
determining which refactorings are necessary, applying them,
and most importantly - preserving the code behavior while doing all these.


Inside the book
---------------

**Chapter 1** pulls the reader straight into refactoring example.
This chapter is `available for free download <https://www.thoughtworks.com/content/dam/thoughtworks/documents/books/bk_Refactoring2-free-chapter_en.pdf>`__.
Before diving into the code, the author discusses the reasons for refactoring.
After all, a compiler doesn't care about the quality of our code.
It has no aesthetic judgement.
We like clean code because it is easier to comprehend and change.

..

  A poorly designed system is hard to
  change—because it is difficult to figure out what to change and how these changes
  will interact with the existing code to get the behaviour I want. And if it is hard
  to figure out what to change, there is a good chance that I will make mistakes
  and introduce bugs.

Fowler teaches how to improve the code without breaking it -
in tiny, explicit, consequential steps.
He emphasises the **tests** as the cornerstone of successful refactoring.
If a piece of code has no tests, it's hard to tell whether its observed
behaviour changed after refactoring.

..

  When you have to add a feature to a program but the code is not structured
  in a convenient way, first refactor the program to make it easy to add
  the feature, then add the feature.


**Chapter 2 - "Principles in Refactoring"**,
discusses *why* and *when* we should refactor, the problems
and benefits of refactoring, its relationship to the software
development process in general and dozens of other aspects that one would
not even imagine.
This chapter also aids in explaining refactoring to а wide circle of people,
from junior developers to senior managers.


**Chapter 3 - "Bad Smells in Code"**, is written in cooperation with Kent Beck.
While Chapter 2 talks of *the right time to refactor*,
the third chapter describes the looks and smells of code that is crying for refactoring.
Best of all - the chapter is in plain English - not a single line of code in it!
*"Global data"*, *"Repeated switches"*, *"Temporary field"*,
and many more - I bet you've met them before.


**Chapter 4 - "Building Tests"**, explains the value of self-testing code and
why effective refactoring is impossible without a reliable test suite.

..

  Refactoring is a valuable tool, but it can’t come alone.
  To do refactoring properly, I need a solid suite of tests to spot my inevitable
  mistakes.
  Even with automated refactoring tools, many of my refactorings will still need
  checking via a test suite.

The Catalogue
.............

The rest of the book is a monumental catalogue of refactorings.
There are six chapters with more than 60 refactorings thoroughly broken down.
Fowler starts with a mix of refactorings that he considers the most useful and common,
such as "Extract function", "Rename Variable", "Introduce Parameter Object".
Every following chapter reveals a group of related refactorings.

Each refactoring is presented in a standard format:

1. **Name**. The name is important to building a vocabulary of refactorings.
   Fowler refers to a refactoring by its name elsewhere in the book.
2. **Sketch**. The sketch shows a small code example of the transformation of the refactoring.
   It does not explain what a refactoring is but
   helps to understand and recognise a refactoring quickly.
3. **Motivation**. The motivation describes why the refactoring should be done
   and the circumstances in which it should **not**. While it's possible
   to deal with a code smell via different refactorings, this section
   describes the "flavour" of a code smell that requires the given refactoring.
4. **Mechanics**. The mechanics are a concise, step-­by-­step description of
   how to carry out the refactoring.
5. **Example**. The examples show how to apply the refactoring in code.

It's worth mentioning that the online catalogue of refactorings with
names and sketches is available for free at
`<https://www.refactoring.com/catalog/>`_!


Reading the book
................

This book primarily appeals to seasoned developers.
One has to write thousands and read tens of thousands of lines of code before
she is able to detect code smells effortlessly.
The book won't make much sense for a junior developer
making his first steps in programming.

Most of the refactorings would look familiar for the developers that
have been around the block.
Challenge yourself by trying to describe the exact mechanics of a refactoring before reading them.
I failed for almost all the refactorings, missing (not even realising) some steps
every time!
The examples help to map everything you've just learned about a refactoring
to real code.
It might be tedious to read every example section thoroughly -
after all, those are paper-printed code blocks.
But the book won't be complete without them.


Thoughts
........

After I finished reading the book I felt that all my prior practical knowledge
and experience has been "rebased" on a solid theoretical foundation.
The book vocabulary is a ubiquitous language of the refactoring domain and
makes it so much easier to explain your intentions to colleagues
- especially when they also use the same vocabulary.
I highly recommend this book to software professionals
who want to improve and formalise their refactoring skills.
