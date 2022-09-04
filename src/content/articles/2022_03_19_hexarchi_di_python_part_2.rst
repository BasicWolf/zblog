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

Now that you are familiar with the basic principles of Hexagonal architecture
(see Part I of the series TODO),
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

A Django project can be easily recognized by the top-level structure:

.. code-block:: text

   src/
     hexarch_project/             # Django application essentials: wsgi.py, urls.py, settings.py
     myapp/
       migrations/                # Django migrations
       apps.py                    # Django app configuration (creates dependencies container instance)
       dependencies_container.py  # Dependencies container
       models.py                  # Django DB models (imports models from SPI adapters)
       urls.py                    # Django urls mappings
       ⋮
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
     service/
   ports/             # API and SPI ports (interfaces)
     api/
     spi/
   adapter/           # API and SPI ports implementation
     api/
       http/          # Django views and serializers
       messaging/
       ⋮
     spi/
       persistence/
         entity/      # Django models
         exceptions/  # Generic (django-independent) persistence exceptions
         repository/  # High-level persistence abstraction
       messaging/
       ⋮
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
4. Users can vote for an article only if their "karma" (i.e. user rating) value is high enough, greater than 5.
5. A user can vote once per article.

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
Actually this view is pretty simple to test.
The only dependency here is an object which implements ``VoteForArticleUseCase``
protocol TODO:source:

.. code-block:: python

   class VoteForArticleUseCase(Protocol):
      def vote_for_article(self, command: VoteForArticleCommand) -> VoteForArticleResult:
          raise NotImplementedError()


We can test all the possible scenarios by injecting a tailored test double.
This is times more lightweight compared to traditional Django app testing.

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
Does it take much effort to grok it?
Did you notice how we test the view without touching the rest of the application?
Have you also noticed that it takes only five lines of code (three, if you put the
``return`` on a single line!) to mock "the rest of the application"?
There is no need to patch anything.
Suddenly the responsibilities in an application are decoupled.
Suddenly, we don't have to set up a database or *any* other part of the application
to test how an HTTP endpoint works.


Application service: a skeleton
===============================

Application services are the conductors that orchestrate processes and data flow in the application.
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

You may have started wondering what ``VoteForArticleResult`` and ``SuccessfullyVotedResult`` are.
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

The domain layer encapsulates business logic and business processes.
Developers and business experts greatly benefit when they share understanding and call a spade a spade.
On the code side, the language used in the names of classes, methods
and other code units should resemble the terms from the problem domain.
By looking at such code you can always tell its relation to the problem domain.

Back to the voting for an article, a vote can be represented via an enumeration
(TODO:source):

.. code-block:: python

   class Vote(Enum):
       UP = 'up'
       DOWN = 'down'

Karma is an explicit type alias (todo:source):

.. code-block:: python

   Karma = NewType('Karma', int)


The most complex class of our domain is ``VotingUser``.
It represents a user that is voting or has already voted for an article
and implements vote casting for an article routine.
We use ``Karma`` value to decide whether the user can vote.
We also need to know whether the user has already ``voted``.
Voting for an article produces a ``result``: (TODO:source)

.. uml::

   @startuml
   class VotingUser {
       id: UserId
       karma: Karma
       votes_for_articles: List[ArticleVote]

       +vote_for_article (article_id: ArticleId, vote: Vote) -> VoteForArticleResult
   }

   @enduml

It is imperative to use domain language in the implementation.
Even the private methods ``_user_voted_for_article()`` and ``_karma_enough_for_voting``
follow the domain language. A fellow developer could easily map the code back
to the domain model and business rules.

.. code-block:: python

   @dataclass
   class VotingUser:
       id: UserId
       karma: Karma
       votes_for_articles: list[ArticleVote] = field(default_factory=list)

       def vote_for_article(
           self,
           article_id: ArticleId,
           vote: Vote
       ) -> VoteForArticleResult:
           if self._user_voted_for_article(article_id):
               return AlreadyVotedResult(article_id, self.id)

           if not self._karma_enough_for_voting():
               return InsufficientKarmaResult(user_id=self.id)

           ## IMPORTANT! The model state changes! ##
           self.votes_for_articles.append(
               ArticleVote(article_id, self.id, vote)
           )

           return SuccessfullyVotedResult(article_id, self.id, vote)

       ...

So far we have implemented the domain model behavior. What's missing is how the
model is constructed. Where does the application service gets the model instance?
It's time to define our first SPI port.


SPI Ports
=========

In Hexagonal Architecture, an application service communicates with the outer world
via Service Interface Provider (SPI) ports. We usually call them "Interfaces" :)
In our example, the application service fetches the users by ``user_id`` and ``article_id``.
That can be expressed as a ``FindVotingUserPort`` (TODO:source):

.. code-block:: python

   class FindVotingUserPort(Protocol):
       def find_voting_user(self, article_id: ArticleId, user_id: UserId) -> VotingUser:
           raise NotImplementedError()

The article service takes ``FindVotingUserPort`` into use as a dependency.
In practice, we add a respective field and a way to initialize it, e.g. through
service constructor:

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
           self._find_voting_user_port = find_voting_user_port

Can you tell, what actual implementation is behind that interface?
Is ``VotingUser`` found from a file? A database? Perhaps another HTTP endpoint?
Or a hard-coded value?
The application service does not care. It just makes a call:

.. code-block:: python

   class ArticleRatingService(...):
       def vote_for_article(self, command: VoteForArticleCommand) -> VoteForArticleResult:
           voting_user = self._find_voting_user_port.find_voting_user(
               command.article_id,
               command.user_id
           )
           ...

The service still has one more thing to do. It has to persist the voting results.

It terms of DDD, ``VotingUser`` is an `aggregate root <https://martinfowler.com/bliki/DDD_Aggregate.html>`.
To update an article rating we have to persist a ``VotingUser`` as a whole.
``SaveVotingUserPort`` takes care of that (todo:source):

.. code-block:: python

   class SaveVotingUserPort(Protocol):
       def save_voting_user(self, voting_user: VotingUser) -> VotingUser:
           raise NotImplementedError()


Putting the service pieces together
===================================

Finally, ``ArticleRatingService`` has all the bits and pieces required to orchestrate
the use case:

.. code-block:: python

   class ArticleRatingService(
       VoteForArticleUseCase
   ):
       _find_voting_user_port: FindVotingUserPort
       _save_voting_user_port: SaveVotingUserPort

       ...

       def vote_for_article(self, command: VoteForArticleCommand) -> VoteForArticleResult:
           voting_user = self._find_voting_user_port.find_voting_user(
               command.article_id,
               command.user_id
           )

           voting_result = voting_user.vote_for_article(
               command.article_id,
               command.vote
           )

           match voting_result:
               case SuccessfullyVotedResult():
                   self._save_voting_user_port.save_voting_user(voting_user)

           return voting_result

First the service gets the ``VotingUser`` which is supposed to vote for the article.
Next, the user votes for the article.
Last, the service checks whether user has successfully voted and persist the user state.

.. note::

   Do you remember that an application service is supposed to orchestrate
   the flow without any knowledge of its content?
   You may have noticed, that our application service does not fulfill this
   requirement. The service makes controls the flow in ``match voting_result:`` block.
   I had to cheat here to make the code easier to follow and comprehend.
   One of the purer alternatives is domain events mechanism.
   (TODO:link-to-some-article) It is a separate topic which falls out of the scope of this article.


Test-driven application services development
============================================

I bet you know what's been happening behind the scenes of writing every bit
of the example code. For every written piece, I've been first asking myself
"How can this be tested?". And tests always came first.

There is a catch with application service testing. It requires quite a few
test doubles - one per each dependency.
That doesn't make testing hard.
If we hide all the required data fixtures behind meaningful names, the
tests become quite obvious. Here, we test that the service persists the
voting user (TODO:source).


.. code-block:: python

   def test_voting_user_saved(
       self,
       vote_for_article_command: VoteForArticleCommand,
       saved_voting_user: VotingUser
   ):
       save_voting_user_port_mock = SaveVotingUserPortMock()
       article_rating_service = build_article_rating_service(
           save_voting_user_port=save_voting_user_port_mock
       )

       article_rating_service.vote_for_article(vote_for_article_command)

       assert save_voting_user_port_mock.saved_voting_user == saved_voting_user




What's next
===========

This concludes the Part II of the article series about Hexagonal Architecture
and Python and Django.
Part III will discuss how to use Django Models in SPIs, manage database
transactions and put all the application pieces together. Stay tuned!


References
==========

.. [#] `Domain-Driven Design <https://en.wikipedia.org/wiki/Domain-driven_design>`_
