Hexagonal architecture and Python - Part II: Domain, Ports and Application Services
###################################################################################

:slug: hexarch_di_python_part_2
:categories: Articles
:tags: architecture, DDD, dependency injection, hexagonal architecture, programming, python,
:date: 2022-03-19 12:00
:summary: Welcome to the second part of the article series, which cover principles of
          Hexagonal architecture, Dependency Injection, Domain-Driven Design and applies
          these all to Python and Django application design.
:status: draft

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

The application *directory* structure though goes way deeper.
From Python perspective, all directories under ``application/`` are **namespace-packages**
i.e. there is no ``__init__.py`` in them.
The namespace packages allow **the tests package structure to follow the application packages structure**.

The core of a Django application designed by hexagonal architecture principles can be structured as follows:

.. code-block:: text

   domain/            # Business domain models, events and services
     event/
     model/
   ports/             # API and SPI ports (interfaces)
     api/
     spi/
   adapter/           # API and SPI ports implementation
     api/
       http/          # Django views and serializers
     spi/
       persistence/
         entity/      # Django models
         exceptions/  # Generic (django-independent) persistence exceptions
         repository/  # High-level persistence abstraction
   service/           # Application services

Notice that Django is present only in adapters.
Django Views are ``HTTP API`` adapters and Django Models are
``Persistence SPI`` adapters.
The rest of the project is indepenendent from the framework.

Use case: Upvote an Article
===========================

Now, let's take a look at an example use case.
Imagine that we are developing a web blogging platform.
The next big thing is the ability for the platform users to vote for articles.
We have discussed the use case with the end-users, platform experts, and other stakeholders and agreed on a minimally viable solution.
Our initial plan is fairly simple:

1. Every article has a rating.
2. The rating can be changed by the users.
3. To change the rating, a user either "upvotes" or "downvotes" the article.
4. A user can vote for an article only if "karma" (i.e. user rating) value is high enough, greater than 5.
5. A user can vote for each article only once.

Where do we start?
==================

That's a simple question, isn't it?
Let's consider our options:

1. **Domain**? By developing domain model we could quickly find out how well the
   mental domain model is expressed in code.

   The problem here is that application users would not be able to try
   whatever we've been building here.
   Since it's pure domain layer development, it doesn't interact with the outer
   world yet.

   It seems that integration points have to go first. Which ones?

2. **Database**. It is important to integrate early to the services
   an application depends upon. We could use mocks and mocked interfaces
   from start, but they won't be enough in a long run.
   The invisible bottlenecks of the real systems could bring unpleasant surprises
   if integration is postponed till the last moment.

   That being said, could OUR application provide its public integration
   points sooner?

3. **Public API**. Public API is our contract with the outer world.
   We would collaborate with the API consumers and **design it together**.
   Once the API is defined, consumers and producer (our service) can
   implement their part of the contract independently.
   This doesn't mean that we have to release the application only when
   the use case is fully implemented.
   Quite the contrary, spinning up the bare bone application with active API
   endpoints allows the consumers to start the integration process immediately.
   At first, the API would respond with stubbed data.
   Despite the business logic missing, the application would be "alive, up and running"
   to the outer world.
   We would get immediate feedback about the quality of our API from the consumers.


HTTP API
========

It won't surprise you that the proposed specification is RESTful API.
Let's use OpenAPI 3.0 specification to make a sketch of the new endpoint:

.. code-block:: yaml

   paths:
     /article_vote:
       post:
         summary: Vote for an article.

         requestBody:
           required: true
           content:
             application/json:
               schema:
                 $ref: '#/components/schemas/Vote'

         responses:
           '201':
             summary: Voted successfully.
           '400':
             summary: Bad request. There was a domain constraint violation.
           '409':
             summary: Conflict. User has already voted.

.. note::

   We are deliberately omitting the complete specification since
   the topic is out of this article's scope.

Django Rest Framework is the obvious choice to facilitate a RESTful endpoint
implementation with Django.
Beside the request and response processing, the logic fits into few lines
of code: TODO-source

.. code-block:: python

   class ArticleVoteView(APIView):

       def __init__(self, vote_for_article_use_case: VoteForArticleUseCase):
           self.vote_for_article_use_case = vote_for_article_use_case
           super().__init__()

       def post(self, request: Request) -> Response:
           vote_for_article_command = self._read_command(request)
           result = self.vote_for_article_use_case.vote_for_article(
               vote_for_article_command
           )
           return self._build_response(result)

       ...

The intentions here are:

1. Accept the HTTP request, deserialize and validate the request data.
2. **Invoke the use case**.
3. Serialize the result and render the response.

I should emphasize that in real life, the tests should always come first.
How easy is to test this view?
The only dependency here is an object which implements ``VoteForArticleUseCase``
protocol:

.. code-block:: python

   class VoteForArticleUseCase(Protocol):
      def vote_for_article(self, command: VoteForArticleCommand) -> VoteForArticleResult:
          raise NotImplementedError()


We can test all the possible scenarios by injecting a tailored test double.
This is times more lightweight compared to traditional Django apps testing,
when we have to connect to a database, even if it is only in memory.

For example, how would we test a scenario, where a user tries to vote twice?
TODO-source:

.. code-block:: python

   def test_post_article_vote_with_same_user_and_article_id_twice_returns_conflict(
       arf: APIRequestFactory
   ):
       ## This is *the* view we are testing
       article_vote_view = ArticleVoteView.as_view(
           ## we are injecting a stub which always
           ## returns AlreadyVotedResult (see below)
           vote_for_article_use_case=VoteForArticleUseCaseAlreadyVotedStub()
       )

       ## A valid article vote is POSTed
       response: Response = article_vote_view(
           arf.post(
               '/article_vote',
               {
                   'user_id': UserId(UUID('a3854820-0000-0000-0000-000000000000')),
                   'article_id': ArticleId(UUID('dd494bd6-0000-0000-0000-000000000000')),
                   'vote': Vote.UP.value
               },
               format='json'
           )
       )

       ## But the result is HTTP 409, as defined in the specification
       assert response.status_code == HTTPStatus.CONFLICT
       assert response.data == {
           'status': 409,
           'detail': "User \"a3854820-0000-0000-0000-000000000000\" has already voted"
                     " for article \"dd494bd6-0000-0000-0000-000000000000\"",
           'title': "Cannot vote for an article"
       }

And here is the ``VoteForArticleUseCaseAlreadyVotedStub``:


.. code-block:: python

   class VoteForArticleUseCaseAlreadyVotedStub(VoteForArticleUseCase):
       def vote_for_article(self, command: VoteForArticleCommand) -> VoteForArticleResult:
           return AlreadyVotedResult(
               user_id=command.user_id,
               article_id=command.article_id
           )

I'm asking you to pause for a moment and read the test code thoroughly.
Do you understand it? Do you see that the view is being tested without
the rest of the application?
Have you noticed that it takes only five lines of code (three, if you put the
``return`` on a single line!) to mock "the rest of the application"?
And there is no need to patch anything.
Suddenly the responsibilities in an application are decoupled.
Suddenly, we don't have to set up *everything*, including a DB to test how an
HTTP endpoint works.



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

How would you model this use case?
To count an article rating, the system should be certain of who and how voted for each article.
This already requires three domain concepts: *User Identity*, *Article Identity* and *Vote Value*.
What about constraints?
To vote, a user should have enough *karma*.
There should also be a mechanism to prevent a user to vote multiple times.


A ``VotingUser`` class is a read-only entity.
It represents a user that is voting or has already voted for a certain article.
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
