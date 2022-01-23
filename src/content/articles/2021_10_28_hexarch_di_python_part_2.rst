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
What about the other web frameworks, like FastAPI, Flask, AIOHTTP with SQLAchemy or a NoSQL data store?

Hexagonal architecture painlessly decouples the business logic from the technical details of
HTTP communication, file system and database access, messaging and so on.
You can swap Django WSGI application with FastAPI.
You can get rid of Django ORM and go with SQLAlchemy.
Not a single line of business logic code would be altered.

The full source of the example is available at `github repository <https://github.com/BasicWolf/hexagonal-architecture-django>`_.

.. tip:: Checkout the repository before continuing. The layered hexagonal architecture
         means deeply nested sub-packages. It's more comfortable to navigate when you have the code locally.

Project structure
=================

On the surface, the project structure looks like the following:

.. code-block:: text

   src/
     hexarch_project/
     myapp/
       migrations/                # Django migrations
       apps.py                    # Django app configuration (creates dependencies container instance)
       dependencies_container.py  # Dependencies container
       models.py                  # Django DB models (imports models from SPI adapters)
       urls.py                    # Django urls mappings

       eventlib/                  # minimalistic domain events dispatcher
       application/               # application code; structure follows hexagonal architecture
         adapter/                 # API and SPI ports implementation
         domain/                  # Business domain
         ports/                   # API and SPI ports (interfaces)
         service/                 # Application services
         util/                    # strictly necessary utility code

The application *directory* structure though goes way deeper.
From Python perspective, all directories under ``application/`` are **namespace-packages**
i.e. there is no ``__init__.py`` in them.
The namespace packages allow **the tests package structure to follow the application packages structure**,

An application can be bootstrapped with the following directories tree:

.. code-block::
   adapter/
     api/
       http/          # Django views and serializers
     spi/
       persistence/
         entity/      # Django models
         exceptions/  # Generic (django-independent) persistence exceptions
         repository/  # High-level persistence abstraction
   domain/
     event/
     model/
   ports/
     api/
     spi/
   service/



Use case: Upvote an Article
===========================

Imagine that we are developing a web blogging platform.
The next big thing is the ability for the platform users to vote for articles.
We have thoroughly discussed the needs with the users, platform experts, and other stakeholders and agreed on a minimally viable solution.
Our initial plan is fairly simple:

1. Every article has a rating and can be "upvoted" or "downvoted".
2. A user can vote for an article only if their rating (called "Karma") is high enough, greater than 5.
3. A user can vote for each article only once.

The domain
==========

We start with the domain layer.
The domain layer encapsulates the business logic and processes
and detaches them from all technical mumbo-jumbo that has nothing to do with the business.
Following Domain-Driven Design (DDD)\ [#]_ principles, we would match the business language while reflecting the business domain in the code.
DDD advocates that developers should perform domain modelling together with domain experts.
Together, we would also produce a ubiquitous language understood by developers and domain experts alike.
The software pieces' names (modules, classes, functions, methods, even variables) would stick to the terms of ubiquitous language and enrich it back.
This time, I had put on both hats of a developer and a domain expert.
Multiple domain modelling iterations later, the following emerged:

A ``VotingUser`` class is a read-only entity.
It represents a user that can vote for an article.
We use ``Karma`` value to decide whether the user can vote.
We also need to know whether the user has already ``voted``.
Voting for an article produces a ``result`` and might emit some ``domain events``.
Here is the model structure:

.. uml::

   @startuml
   class VotingUser {
       id: UserId
       karma: Karma
       voted: Boolean

       +vote_for_article (article_id: ArticleId, vote: Vote) -> (VoteForArticleResult, List[Events])
   }

   @enduml


.. code-block:: python

   pass

References
==========

.. [#] `Domain-Driven Design <https://en.wikipedia.org/wiki/Domain-driven_design>`_
