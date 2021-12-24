Hexagonal architecture of ports and adapters, Dependency injection and Python - Part II
#######################################################################################

:slug: hexarch_di_python_part_2
:categories: Articles
:tags: architecture, DDD, dependency injection, hexagonal architecture, programming, python,
:date: 2021-10-30 22:30
:summary: Welcome to the second part of the article series, which cover principles of
          Hexagonal architecture, Dependency Injection, Domain-Driven Design and applies
          these all to Python and Django application design.

Now that you are familiar with the basic principles of Hexagonal architecture,
let's try implementing a Django-based application following these principles.
I've chosen Django for this exercise to demonstrate that even an opinionated framework is not an obstacle for Hexagonal architecture.
The full source of the example is available at `github repository <https://github.com/BasicWolf/hexagonal-architecture-django>`_.

Upvote an Article
=================

Imagine that we are developing a web blogging platform.
The next big thing to implement is the ability for the platform users to vote for articles.
Our initial plan is fairly simple:

1. Every article has a rating and can be "upvoted" or "downvoted".
2. Every user has a rating too. A user's rating is called **Karma**.
3. A user can vote for an article only if their karma is high enough, greater than 5.
4. Finally, a user can vote for each article only once.


Where do we start?
==================

The domain model is the heart of the application.
By implementing the domain model first, we could discover new domain concepts and events,
potential pitfalls, invariants, and so on.
Be aware that domain modeling is challenging and its design takes multiple iterations before reaching an acceptable state.
I would argue though, that the use case implementation in form of an application service comes first.
Think about it: an application service routes the data from the external call to the domain model and SPI ports.
The application service doesn't have much knowledge of how all these work,
but it knows when and how each actor should be called. Don't mind the missing building blocks like classes and methods.
Start by sketching the service behavior in plain text:

.. code-block:: none

   Use case: a user votes for an article
     essential constraints:
         the article and the user have to exist
     domain rules:
         the user did not vote before
         the user has enough karma to vote
     domain actions:
         user votes for an article
