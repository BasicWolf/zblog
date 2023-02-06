Specification by example - book review
######################################

:slug: specification_by_example_book_review
:category: Books
:tags: book, review, programming, specification, requirements, BDD, collaboration
:date: 2023-02-21 22:17
:status: published
:summary:

   .. image:: {static}specification_by_example_book_cover.jpg
      :alt: "Specification by Example" by Gojko Adzic book cover.
      :align: center

   Doing things right doesn't matter unless you do the right thing.
   "Specification by Example" by Gojko Adzic is about delivering the right
   software. Adzic has interviewed many successful teams and discovered
   that their ways of software development are quite similar.
   These ways or processes are based on a close collaboration between
   all the parties, including business representatives.
   It begins by understanding the business goals.
   It continues with creating a specification and utilizing it for
   software development and verification.
   It is finalized by providing living documentation which reflects
   the current software state and behaviour.

   "Specification by Example" helped me to understand how to do
   behaviour-driven development (BDD).
   It is an excellent reading for a software craftsman.

.. image:: {static}specification_by_example_book_cover.jpg
   :alt: "Specification by Example" by Gojko Adzic book cover.
   :align: center


Merriam-Webster dictionary
`defines <https://www.merriam-webster.com/dictionary/specification>`_
*specification* as

..

  1. The act of specifying - naming or stating explicitly or in detail.
  2. A detailed, precise presentation of something or a plan or proposal
     for something.

I think of specification as
*a definition of what the system is expected to do*.
Ah, if only systems always behaved as they were supposed to!

You darn well know, how that happens.
First comes the business, with brilliant or not-so ideas.
"We are going to make a new product! It will increase our revenue! ...
[an hour later] and the button text should be in red!".
The Business Analysts mince that into a Business case™.
The POs scrutinize the case into user stories.
The QA write acceptance criteria.
Finally, the developers start implementing.
But the business has already given the teams a detailed
vision of how things should be, so there is not much thinking on the way,
just turning JIRA tickets into code. There is even no need to roll it out
in small chunks to the end customer - the business already knows what the
customer wants...
This half a century old illustration has not aged by a single second:

.. image:: {static}computer_centre_treeswing_pictures.jpg
   :align: center
   :alt: The Swing - from the University of London Computer Centre Newsletter No. 53, March 1973


Gojko Adzic analyzed the software industry fallacies that lead to such a result.
He found out that *how* companies deal with these fallacies is very
much alike. The methods and processes are shared by the most successful teams that he interviewed
while researching for the book.
He talks of these methods as *a set of process patterns that facilitate change in software
products to ensure the right product is delivered effectively.*

The foundation of every key pattern is **collaboration**.
Gojko noticed that the "handover" journey of specifications through business people,
product managers, developers, and QA is full of misunderstanding, ambiguity, information losses,
errors and unnecessary work.
"*Specification by example*" teaches how to build a shared understanding between
everyone involved the software creation process.
It then demonstrates how to translate the shared understanding into specification
documents, leverage them for continual system testing, and produce up-to-date
documentation that evolves with the system.

Key process patterns in a tiny nutshell
=======================================

A successful team begins by *deriving scope from a customer's business goals*.
They collaborate to define the scope that will achieve the goal.
The business representatives explain the intent and the value of the feature,
so that everyone understands what's needed. Then, the team works with the business
to determine the solution.

The teams collaborate and specify the solution together with the business people.
*Specifying collaboratively* allows to utilize the expertise of stakeholders,
gather different ideas about the solution and make everyone more engaged.

The stakeholders tightly work together to *illustrate specifications using examples*.
They identify the *key examples* which unambiguously define *what* the software needs to do.
They’re both the target for development and serve an evaluation criterion
to see whether the development is done.

.. image:: {static}key_process_patterns.png
   :align: center
   :alt: Key process patterns


Key examples are a great starting point for creating specification, but
they are not specification yet. Gojko emphasizes, that the common reason
for teams to fail with Specification by Example - is not taking the time to
process the raw key examples.
Successful teams don’t use raw examples; they *refine the specification* from them.
The teams carve out the essence of a key example, discard the unnecessary
details and turn it into a clear definition of the desired system behaviour.

.. note::

   Ideally, a specification with examples should unambiguously define the
   required functionality from a business perspective
   *but not how the system is supposed to implement it*.

   **A good specification, with examples, is effectively an acceptance test for
   the described functionality.**

*Automating the validation process* is a proven way to avoid the bottlenecks of
manual testing.
What's important is that the teams validate *without changing specifications*.
Otherwise, all the value of refining specifications is lost.
Such automated, comprehensible and accessible to all the team members
specification with examples becomes an *executable specification*.

When the validation process happens frequently, the stakeholders are sure
that the software works according to the specification.
However, how and in which form can they access the verification results?
Hence the team continues sharpening the executable specifications and organises
the verification output to provide all the stakeholders with a consistent,
easy-to-understand and up-to-date *living documentation*.


Thoughts
========

Specification by Example is Behaviour-Driven Development. Gojko Adzic
avoided the term since it was too ambiguous, and the meaning changed all the time.
It's been almost fifteen years later since the book was written,
and BDD is still ambiguous and misunderstood by large and small companies alike.

In one company, the team was participating in meetings with the clients, and
together they derived scope from the business goals. They even documented
key examples that the customer provided. But it never went further - the
specifications were extracted to JIRA tickets hierarchy and remained there
never to be seen again, once the tickets got closed.

In another company, the user stories were extracted into Cucumber-based behaviour tests.
But these tests got written AFTER the implementation in code!
They have reflected how developers implemented the software, not how it was supposed
to behave.

The third company used Cucumber for contract testing of HTTP API.
That nicely fits into "101 ways of abusing Given, When, Then".

Least to say, that none of these companies had living documentation.

That is what "Specification by Example" is about. Throughout the book, Gojko
constantly refers to companies and people who explain the key patterns in detail.
The last six chapters of the book are the case studies which tell the story
of real companies and their journey from  waterfall and "agile-ish" development
processes to specification by example.

To my shame, I have yet to build a system that incorporates all the key patterns
described in the book. And I am eagerly looking forward to it!
