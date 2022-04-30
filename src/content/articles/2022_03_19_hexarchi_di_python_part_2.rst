Hexagonal architecture and Python - Part II: Domain,  Application Services, Ports and Adapters
##############################################################################################

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

2. **Database**? It is important to integrate early to the services
   an application depends upon. We could use mocks and mocked interfaces
   from start, but they won't be enough in a long run.
   The invisible bottlenecks of the real systems could bring unpleasant surprises
   if integration is postponed till the last moment.

   That being said, could OUR application provide its public integration
   points sooner?

3. **Public API**? Public API is our contract with the outer world.
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
of code: TODO:source

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
protocol TODO:source:

.. code-block:: python

   class VoteForArticleUseCase(Protocol):
      def vote_for_article(self, command: VoteForArticleCommand) -> VoteForArticleResult:
          raise NotImplementedError()


We can test all the possible scenarios by injecting a tailored test double.
This is times more lightweight compared to traditional Django apps testing,
when we have to connect to a database, even if it is only in memory.

For example, how would we test a scenario, where a user tries to vote twice?
TODO:source:

.. code-block:: python

   def test_user_votes_for_the_same_article_returns_conflict(
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

Please pause for a moment and read the test code thoroughly once again.
Is it easy or hard to grock it?
Notice how we test the view without touching the rest of the application?
Have you also noticed that it takes only five lines of code (three, if you put the
``return`` on a single line!) to mock "the rest of the application"?
There is no need to patch anything.
Suddenly the responsibilities in an application are decoupled.
Suddenly, we don't have to set up *everything*, including a database
to test how an HTTP endpoint works.


Application service: a skeleton
===============================

Application services are the conductors orchestrating processes and data flow in the application.
An application service implements one or more related use cases and invokes
all the necessary dependencies required to perform these use cases.
The service implementation can start with a single return statement only:

.. code-block:: python

   class ArticleRatingService(
       VoteForArticleUseCase
   ):
       def vote_for_article(self, command: VoteForArticleCommand) -> VoteForArticleResult:
           return SuccessfullyVotedResult(
               command.article_id,
               command.user_id,
               command.vote
           )

You may have started wondering what are ``VoteForArticleResult`` and ``SuccessfullyVotedResult``.
Recall the basics of Hexagonal architecture from Part I:

..

   Dependencies are directed from the outer layers to the inner center.

``VoteForArticleResult`` (TODO:source) is a domain data transfer object model.
It carries the voting result from the innermost application layer - the Domain
to the outermost API adapter layer.
Alternatively, we could have used specialized data transfer objects per layer,
which is, in my opinion, an overengineering.
Not only do they repeat one another, they also have to be cast all the way through the layers.

The service skeleton is ready.
But we can't continue developing it without the bits and pieces which convey the business logic.

The domain
==========

The domain layer encapsulates the business logic and processes.
Developers and business experts greatly benefit when they share understanding and call a spade a spade.
On the code side, the language used in the names of classes, methods
and other code units should resemble the terms from the problem domain.

We would greatly benefit if the language used in names of classes, methods and
other code units resembles the terms from the problem domain.
For example, a vote can be represented via an enumeration (TODO:source):

.. code-block:: python

   class Vote(Enum):
       UP = 'up'
       DOWN = 'down'

Karma is an explicit type alias (todo:source):

.. code-block:: python

   Karma = NewType('Karma', int)


The most complex class of our domain is ``VotingUser``.
It represents a user that is voting or has already voted for a certain article.
``VotingUser`` also puts together the business logic required for making
a vote for an article.
We use ``Karma`` value to decide whether the user can vote.
We also need to know whether the user has already ``voted``.
Voting for an article produces a ``result`` and might emit some ``domain events``:

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

   @dataclass(frozen=True)
   class VotingUser:
       id: UserId
       karma: Karma
       voted: bool

       def vote_for_article(
           self,
           article_id: ArticleId,
           vote: Vote
       ) -> Tuple[VoteForArticleResult, List[Event]]:
           if self.voted:
               return AlreadyVotedResult(article_id, self.id), []

           if not KarmaEnoughForVotingSpecification().is_satisfied_by(self.karma):
               return InsufficientKarmaResult(user_id=self.id), []

           return (
               SuccessfullyVotedResult(article_id, self.id, vote),
               [
                   UserVotedEvent(article_id, self.id, vote)
               ]
           )

Some parts of this might look overcomplicated.
For example, why not put down the "karma should be greater than 5" constraint
directly in the ``if`` condition?
We could, but then the constraint (or specification) becomes the part of ``VotingUser``.
Should the user know whether they can vote?
If that logic piece is separate, it can be changed without affecting the ``VotingUser`` code at all!
What about the ``UserVotedEvent``?
It is easier to explain if we get back to the application service level.

SPI Ports
=========

Let's continue with ``VoteForArticleUseCase`` implementation.
In Hexagonal Architecture, an application service "talks" defines its
dependencies as Service Interface Provider (SPI) ports.

For example, we need to fetch the ``VotingUser``
based on the data from the ``VoteForArticleCommand`` (TODO:source):

.. code-block:: python

   class FindVotingUserPort(Protocol):
       def find_voting_user(self, article_id: ArticleId, user_id: UserId) -> VotingUser:
           raise NotImplementedError()

The SPI adapters are injected into the service during its initialization:

.. code-block:: python

   class ArticleRatingService(
       VoteForArticleUseCase
   ):
       _find_voting_user_port: FindVotingUserPort
       ...

       def __init__(
           self,
           find_voting_user_port: FindVotingUserPort,
           ...
       )

And the service does not (nor should it) have any idea, what
kind of implementation is behind
the port.
An HTTP service, a database, a file from the local file system,
it could even be a pure Python collection!
At this point, it's enough to have a stub which returns a hard-coded user:

.. code-block:: python

   class FindVotingUserAdapterStub(FindVotingUserPort):
       def find_voting_user(self, article_id: ArticleId, user_id: UserId) -> VotingUser:
           return VotingUser(user_id, Karma(10), voted=False)


Invoking the domain and handling events
=======================================

We can now join and orchestrate the ``FindVotingUserPort`` and the domain
to run the use case:

.. code-block:: python

   class ArticleRatingService(VoteForArticleUseCase):
       _domain_event_dispatcher: EventDispatcher
       _find_voting_user_port: FindVotingUserPort

       def vote_for_article(self, command: VoteForArticleCommand) -> VoteForArticleResult:
           voting_user = self._find_voting_user_port(command.article_id, command.user_id)

           voting_result, events = voting_user.vote_for_article(
               command.article_id,
               command.vote
           )

           for event in events:
               self._domain_event_dispatcher.dispatch(event)

           return voting_result

Note how lean is the body of ``vote_for_article()``.
It carries no logic about what to do with the voting results
Whatever has happened during ``voting_user.vote_for_article()`` can be handled
by whoever is interested in these events.
What if we want to handle ``UserVotedEvent`` right here?
What if we want to persist the vote?
Easy!
We register a method of ``ArticleRatingService`` as the event handler
and invoke an SPI port which saves the vote:

.. code-block:: python

   class ArticleRatingService(VoteForArticleUseCase):
       ...
       _domain_event_dispatcher: EventDispatcher
       _save_article_vote_port: SaveArticleVotePort

       def __init__(...)
           ...
           self._domain_event_dispatcher.register_handler(
               UserVotedEvent,
               self._on_user_voted
           )

       def _on_user_voted(self, event: UserVotedEvent):
           self._save_article_vote_port.save_article_vote(
               ArticleVote(
                   event.article_id,
                   event.user_id,
                   event.vote
               )
           )


How about an alternative to domain events handler?
We need another way of figuring out, whether the vote should be saved or not.
For example:

.. code-block:: python

   voting_result = voting_user.vote_for_article(
      command.article_id,
      command.vote
   )

   if isinstance(voting_result, SuccessfullyVotedResult):
       self._save_article_vote_port.save_article_vote(...)


Besides being ugly, this code also violates the basic principle of our architecture:
Separation of concerns.
Remember, that an application service are meant to orchestrate the flow.
By adding this ``if`` we force the application service to make decisions.
Instead, we should let the service to dispatch the domain events without
caring where, when and how they are handled.

Application service: test-driven development
============================================

Once again, I would like to stress that we use test-driven approach,
though I didn't mention the tests explicitly.
For example, this unit test verifies the "user can vote only once" domain behavior:
(TODO:source)

.. code-block:: python

   def test_vote_for_article_twice_returns_already_voted_result():
       voting_user = build_voting_user(
           UserId(UUID('7ebd50e7-0000-0000-0000-000000000000')),
           voted=True
       )
       result, *_ = voting_user.vote_for_article(
           ArticleId(UUID('2f868ceb-0000-0000-0000-000000000000')),
           Vote.UP
       )
       assert isinstance(result, AlreadyVotedResult)

Think of the corresponding application service tests.
Is there a need to test the same behavior there?
Is there a need to have a unit test which verifies that
``article_rating_service.vote_for_article()`` returns ``AlreadyVotedResult``?
Remember that service doesn't care about the data.
The service is about the data flow.
So, there is only a need to check that the services invokes the domain model as expected:
(TODO:source)

.. code-block:: python

   def test_arguments_passed_to_vote_for_article(self):
       found_voting_user_mock = build_voting_user_mock()

       article_rating_service = build_article_rating_service(
           FindVotingUserPortStub(found_voting_user_mock)
       )
       article_rating_service.vote_for_article(
           build_vote_for_article_command(
               article_id=ArticleId(UUID('ef70ade4-0000-0000-0000-000000000000')),
               vote=Vote.UP
           )
       )

       found_voting_user_mock.vote_for_article.assert_called_with(
           ArticleId(UUID('ef70ade4-0000-0000-0000-000000000000')),
           Vote.UP
       )

In other words, we test that ``VotingUser.vote_for_article(...)`` was called with
the expected arguments.
In order to do that, we hand-craft a ``FindVotingUserPortStub`` test double,
which returns a mocked ``VotingUser``.
We then instantiate ``ArticleRatingService`` and inject this stub into it.
Finally we call ``.vote_for_article()`` and assert our expectation.


I am a proponent of `solitary tests <https://martinfowler.com/bliki/UnitTest.html>`_
when it comes to flow testing.



References
==========

.. [#] `Domain-Driven Design <https://en.wikipedia.org/wiki/Domain-driven_design>`_
