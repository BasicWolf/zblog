Clean Architecture - book review
################################

:slug: clean-architecture-book-review
:category: Books
:tags: book, review, programming, architecture, clean code, clean architecture
:date: 2023-05-18 22:39
:summary:
   .. image:: {static}clean-architecture-book-cover.jpg
      :width: 30%
      :align: center
      :alt: "Clean Architecture" book cover
      :target: {filename}clean-architecture-book-review.rst

   *Clean Architecture* is the "Art of War" of the software industry. It was written by a professional who has been through many tough battles, both wins, and losses. Uncle Bob talks about timeless topics of software development that are just as applicable today as they were fifty years ago.

Oh, I loved the book! A warm picture emerges in my mind: late evening,
comfortable armchairs, a hot burning fire in a fireplace, and an engaging discussion
with a dear friend who happens to be one of the greatest teachers in software engineering...

.. image:: {static}clean-architecture-book-cover.jpg
   :align: center
   :alt: "Clean Architecture" book cover

"Clean Architecture" is the "Art of War" of the software industry.
It was written by a professional who has been through many tough battles, both wins, and losses.
Uncle Bob talks about timeless topics of software development that are
just as applicable today as they were fifty years ago.

Software architecture determines the necessary pieces and their integration to create the desired system.
The pieces can vary from individual variables and functions to large-scale services like databases.

..

  The goal of software architecture is to minimize the human resources required
  to build and maintain the required system.
  The measure of design quality is simply the measure of the effort required to
  meet the needs of the customer.

It is that simple! Or is it?
How many times have you struggled trying to fit a new feature into an existing code base?
How many times have you started from scratch, only to find later that the redesign became the same mess as before?

Here is a scary diagram from the book.
It shows how the cost of each line of code increases with every major release.
This trend is not sustainable; no business model can make a profit while letting costs grow exponentially.

.. image:: {static}market-leading-software-product-life-cycle.png
   :width: 75%
   :align: center
   :alt: Market leading software product life cycle

Why does this happen? What goes wrong?
Too often, we developers buy into the familiar lie:
*"We can clean it up later; we just have to get to market first!"*

..

  Of course, things never do get cleaned up later, because market pressures never
  abate. Getting to market first simply means that you’ve now got a horde of
  competitors on your tail, and you have to stay ahead of them by running
  as fast as you can.

  And so the developers never switch modes. They can’t go back and clean things
  up because they’ve got to get the next feature done, and the next, and the next,
  and the next. And so the mess builds, and productivity continues its asymptotic
  approach toward zero.

Making messes is always slower than staying clean and the only way to go fast,
is to go well.


We often forget that, unlike firmware, software was invented to be "soft."
It was intended to be a way to easily change the behavior of machines.
Therefore, software architectures should be as shape-agnostic as possible.
Uncle Bob argues that for a software system to be easy to change, it is more important than for it to work.

..

  If you give me a program that does not work but is easy to change, then I can
  make it work, and keep it working as requirements change. Therefore the
  program will remain continually useful.

One of our responsibilities is to find the balance and
assert the importance of architecture over the urgency of features.
Sometimes we have to fight for it with the business side that is pushing to implement new features.
If architecture comes last, then the system will become even more costly to develop,
and eventually, change will become practically impossible for a part or all of the system.

That is the end of **Part I - Introduction**.
The rest of the tale is for you to discover, just like in 'One Thousand and One Nights'.

Inside the book
---------------

In **Part II - Starting with the Bricks: Programming Paradigms**, Uncle Bob discusses
structured, object-oriented, and functional programming paradigms,
and how to apply them from an architectural perspective.

Each paradigm is about discipline, telling us what *not* to do, and each paradigm
takes something away from us. Each restricts some aspect of the way we write code.

In **Part III - Design Principles** we learn to put the well-made software
bricks together.

..

  Good software systems begin with clean code. On the one hand, if the bricks
  aren’t well made, the architecture of the building doesn’t matter much. On the
  other hand, you can make a substantial mess with well-made bricks. This is
  where the SOLID principles come in.

  The goal of the principles is the creation of mid-level software structures that:

  * Tolerate change,
  * Are easy to understand, and
  * Are the basis of components that can be used in many software systems.

**Part IV - Component Principles** is about arranging larger software blocks
to make a sound system.

..

  Components are the units of deployment. They are the smallest entities that can
  be deployed as part of a system. In Java, they are jar files. In Ruby, they are gem
  files. In .Net, they are DLLs. In compiled languages, they are aggregations of
  binary files. In interpreted languages, they are aggregations of source files.

  Regardless of how they are eventually deployed, well-designed components always
  retain the ability to be independently deployable and, therefore, independently
  developable.


We learn the principles that help in putting components together. We learn how
to group and separate the components and how to manage dependencies between them.

Finally **Part V - Architecture** and **Part VI - Details**.
So far the book has been preparing us to grok these parts.

..

  The architecture of a software system is the shape given to that system by those
  who build it. The form of that shape is in the division of that system into
  components, the arrangement of those components, and the ways in which those
  components communicate with each other.

Uncle Bob talks about the importance of deferring decisions about details.
Should we use a database or a plain text file? Shall we rely on TCP or UDP?
Do we use React, Vue, or Angular?
He argues that the longer we keep our options open, the more information we can gather
and the more experiments we can conduct to make an informed decision.

The architecture that allows us to delay these decisions establishes clear boundaries between its components.

..

   Software architecture is the art of drawing lines that I call boundaries.

This statement leads the way to **Clean Architectures**, which are

* Independent of frameworks. The architecture does not depend on the existence
  of some library of feature-laden software. This allows to use such
  frameworks as tools, rather than forcing to cram system into their
  limited constraints.
* Testable. The business rules can be tested without the UI, database, web server,
  or any other external element.
* Independent of the UI. The UI can change easily, without changing the rest of
  the system.
* Independent of the database. We can swap out Oracle or SQL Server for
  Mongo, BigTable, CouchDB, or something else.
* Independent of any external agency. The business rules don’t know
  anything at all about the interfaces to the outside world.


.. image:: {static}clean-architecture.jpg
   :alt: Clean Architecture diagram
   :width: 75%
   :align: center
   :target: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html


The hidden gem
--------------

Book appendices are often skipped by the readers. Don't you dare to skip this one,
because it is the hidden gem of the book. **Architecture Archaeology** is
Uncle Bob's life-long software engineering journey. It is a story of creation and
discoveries, of fights and struggle of everything that lead to writing this book.


Thoughts
--------


This is one of the "must-read" for all software engineers. The only question
is, "When?". This book discusses many abstract topics. Unless you are intimately
familiar with software development, it may have little impact on you.
However, when you start interacting with large systems, a time comes when you sense that something is wrong, and you can't simply formalize it.
That's when you know the time has come.
The time to do architecture right.
The time to embrace Clean Architecture.
