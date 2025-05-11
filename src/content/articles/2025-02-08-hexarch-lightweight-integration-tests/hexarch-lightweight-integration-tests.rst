Hexagonal architecture and Python - Part IV: Lightweight integration tests
##########################################################################

:slug: hexarch-python-part-4-lightweight-integration-tests
:category: Articles
:tags: architecture, django, hexagonal architecture, lightweight integration tests, programming, python, testing
# started writing on 2025-02-08
:date: 2025-05-10 18:00
:status: published
:summary: .. image:: {static}hexarch-lightweight-integration-tests.webp
             :align: center
             :alt: Pythons and hexagons with Part IV
             :target: {filename}hexarch-sociable-tests.rst

          It's pretty straightforward to unit test the components
          of an application that follows Hexagonal Architecture.
          The components are part of specific layers, and mocking
          the next dependency layer is usually simple.
          However, this approach means we never test the application
          as a whole and have to rely on expensive integration or
          end-to-end tests to do so.

          We can test the application components in *sociable* manner,
          leaving our components' direct dependencies as-is,
          and pushing the mocks further to the application edges.

          If we push the mocks too far, we end up with
          *lightweight integration tests*.
          Let's explore how we can utilise such tests in a context
          of Django application and what benefits we can reap.



.. image:: {static}hexarch-lightweight-integration-tests.webp
             :align: center
             :alt: Pythons and hexagons with Part IV

* `Part I: Dependency Injection and componential architecture <{filename}../2021_10_30_hexarch_di_python_part_1/2021_10_30_hexarch_di_python_part_1.rst>`_
* `Part II: Domain,  Application Services, Ports and Adapters <{filename}../2022_09_18_hexarch_di_python_part_2/2022_09_18_hexarch_di_python_part_2.rst>`_
* `Part III: Persistence, Transactions, Exceptions and The Final Assembly <{filename}../2022_12_31_hexarch_di_python_part_3/2022_12_31_hexarch_di_python_part_3.rst>`_
* `Part IV: Lightweight integration tests <{filename}../2025-02-08-hexarch-lightweight-integration-tests/hexarch-lightweight-integration-tests.rst>`_
* `The code  <https://github.com/BasicWolf/hexagonal-architecture-django/tree/blog4>`_

Intro
=====

It is very easy to unit test the components of an application
that follows Hexagonal architecture principles. The components
belong to certain layers, and it's quite straightforward to
mock the following dependency layer.
However, the problem with such an approach is that we never
test the application as a whole, and have to rely on expensive
integration or end-to-end tests to do so.

We can test the application components in *sociable* manner,
leaving our components' direct dependencies as-is,
and pushing the mocks further to the application edges.

If we push the mocks too far, we end up with
*lightweight integration tests*.
Let's explore how we can utilise such tests in a context
of Django application and what benefits we can reap.

..

   The original article focused on such "lightweight integration" tests.
   I even dared to call them "sociable"!
   `Jarkko "jmp" Piiroinen <https://github.com/jmp>`_ was very generous to
   thoroughly review the article. He pointed that *sociable tests*,
   rather implies testing a thing within the application core (or "Application" in
   `Alistair Cockburn's definition <https://alistair.cockburn.us/hexagonal-architecture>`_)
   with its neighbours/collaborators. Testing the whole flow by mocking the
   rightmost calls is "sociable tests pushed too far", or as Jarkko put it
   "rather lightweight end-to-end tests".

   The updated article is about exploring the ways to conduct such tests
   in a Django application setup, focusing on the benefits and caveats.

------

.. _hexarch-sociable-tests-part-4:


.. contents:: Table of Contents
    :depth: 1

Time flies (darn, I say that again)!
I wrote the original "Hexagonal Architecture and Python" series
back in 2022, which was only three years ago
(*honestly, it feels like yesterday!*)
Since then my understanding of RESTful API design and Domain-Driven Design
has deepened. But the biggest shift, however, has occurred in where I start
and how I test.

I used to believed that the *implementation* of the domain model should precede
exposing any API. I still *design* the domain model first before deriving API structure
from if. However, I *implement* barebones API first, initially hard-coding and
short-circuiting domain logic, to enable early integrations and
feedback.
This approach helps steer the development in the right direction,
keeps API consumers happy and avoids "big bang" release surprises.

This led to the second change. I used to TDD every layer and every component
of the application *independently*. Today, I aim at unit testing the
interconnected parts of the system.

Bear in mind, that the system users often don't care about what's happening
under its hood.
They are more concerned with the system's public contract - its behaviour
when queried and commanded through the public interfaces.
System developers, on the other hand, also need assurance that the system
interacts with its downstream dependencies as expected.
We can apply behavior testing similarly: by testing
the system via its public interfaces and downstream interactions,
we reduce the need to test the application layers in isolation.

Just so we're clear, I'm not calling anyone to put the whole thing together
and test it on the launch pad. That's a recipe for disaster - remember what
happened to the
`Soviet N1 Moon rocket <https://en.wikipedia.org/wiki/N1_(rocket)>`__?

..

  Adverse characteristics of the large cluster of thirty engines and its complex
  fuel and oxidizer feeder systems were not revealed earlier in development
  because static test firings had not been conducted.
  (`Wikipedia <https://en.wikipedia.org/wiki/N1_(rocket)>`__)

Instead, I'm looking for relatively lightweight ways to test the entire
system, without going for a full end-to-end setup.


Hexagonal architecture - as described in the articles series
============================================================

Let's recall the application and its architecture as described
in the articles series:

.. figure:: {static}full-app.svg
   :align: center
   :alt: A hexagonal architecture application diagram
   :width: 100%

   The example application is built using hexagonal architecture principles.
   This is beyond what Alistair Cockburn describes in the original
   `"Hexagonal Architecture" article <https://alistair.cockburn.us/hexagonal-architecture>`_.
   Cockburn only defines **Ports**, **Adapters**, **Application** and their
   interactions.


The **Application** has a layered structure: the Core, which includes Domain
models and services; The driving/in/API (application programming interface)
and driven/out/SPI (service provider interface) ports for incoming and outgoing interactions;
and API and SPI adapters.

Python wise:

* The **Domain model** consists of classes and methods which reflect
  the real world domain rules. They are "pure" in nature, because
  they don't have any outer world dependencies.

* We can think of **API** and **SPI ports** as delegates - basically, function signatures.
  We can use Python Protocols or Abstract Base Classes to define them in
  OOP-compatible way.

* The **Application Services** implement API ports and orchestrate the flow
  between domain models and SPI ports. They invoke SPI ports and can also
  invoke other API ports when necessary.

* The **SPI adapters** implement SPI ports. SPI adapters are the bridges between
  the application and downstream dependencies (databases, cashes, message queues,
  file systems, other services etc.)

* The **API adapters** connect the outer world to the application.
  They receive commands and queries through different channels
  (command line, http, RPC, message queue etc.) and invoke API ports.
  The same API port can be invoked by many adapters - think of making the same
  query via a command line, or via a RESTful HTTP interface.

Testing the application
=======================

Martin Fowler speaks of **"Solitary"** and **"Sociable"** tests in the renowned
`article "Unit Test" <https://martinfowler.com/bliki/UnitTest.html>`_.
Solitary tests mock the *direct dependencies* of the component under test.
This is how I originally implemented tests in the
"Hexagonal Architecture with Django" project.
Tests like these run blazingly fast, but they only test the isolated behaviour
of a given component (like an HTTP controller, an application service,
or a database entities mapper) with fake downstream layer interactions.

.. figure:: {static}api-solitary-test.svg
   :align: center
   :alt: A diagram of solitary API test
   :width: 100%

   A mockist-style HTTP adapter test.

Defining sociable tests is trickier:

..

  When xunit testing began in the 90's we made no attempt to go solitary unless
  communicating with the collaborators was awkward
  (such as a remote credit card verification system).

  I think that the term “unit testing” is appropriate because these tests
  are tests of the behavior of a single unit.
  We write the tests assuming everything other than that unit is working correctly.

  -- Martin Fowler, `"Unit Test" <https://martinfowler.com/bliki/UnitTest.html>`__.

So, in my perspective *a unit test is sociable when it verifies a unit of behaviour
across multiple components boundaries. In the verified interaction, at least
one direct dependency is not mocked, however the further dependencies can be mocked.*

.. figure:: {static}api-sociable-test.svg
   :align: center
   :alt: A diagram of sociable API test
   :width: 100%

   A classical-style HTTP adapter test.


Finally, we utilise higher-level integration or end-to-end tests to verify the behaviour flow throughout the application and its dependencies.
Nowadays, tools such as `Testcontainers <https://testcontainers.com/?language=python>`__
allow the isolation of these tests by spinning up the real databases, caches
and other dependencies for a short test lifetime.
However, this setup might be too resource-intensive, or other downstream dependencies,
that cannot be dockerised may need to come into play.
This leaves us with slow and fragile classical e2e tests in an
integration environment.

What if we push sociable tests a bit further?
We can mock the layer which stands between our adapters and external dependencies.
This ensures that an API test flow passes forward
and back through the whole application
in a deterministic and isolated environment:


.. figure:: {static}api-lightweight-integration-test.svg
   :align: center
   :alt: A diagram of a lightweight integration API test.
   :width: 100%

   A lightweight integration test.



Architecture revised
====================

Software architecture is important because it allows us to independently evolve
different parts of the application and delay decisions.
In a way, architecture constrains us, but helps keep the system organised.

My presentation of Hexagonal Architecture in this series of articles,
especially the testing part, was a bit bloated.
Alistair Cockburn
`said nothing <https://alistair.cockburn.us/hexagonal-architecture>`_
about the application's (core) internals.
It's up to us whether we introduce "Service", "Domain" or any other layer
or concept.
Just think: if an HTTP adapter handles a GET request to return
raw data from a single table in the database,
why even bother with "Service" and "Domain" layers
which would only perform data transformations?

So, when it comes to lightweight integration testing,
we leave the application core as a black box,
and interact with adapters only.

.. figure:: {static}hexagonal-core.svg
   :align: center
   :alt: A hexagonal architecture application diagram
   :width: 100%

   We are free to implement the application core in any way
   when applying Hexagonal Architecture principles.


Lightweight integration tests -driven development
=================================================

A classical end-to-end test is a poor development driver.
It takes minutes, sometimes tens of minutes to run, often breaks,
has a complicated setup, and ... (your favourite fallacies here).
A lightweight integration test is somewhat better: it's fast
and fully under our control.
However, it rather drives adapters development,
**NOT** the application core development.
It also requires a complicates setup, especially when it comes
to test doubles.

Nevertheless, let's explore how such a test drives implementation.
What steps would we take?

1. Pick a behaviour unit.
2. Write a test for its API, asserting only the response.
3. Write a minimal implementation to pass the test.
4. If the behaviour is not pure and hits downstream dependencies,
   write a test similar to (2), but **this time verify the dependency interaction.**
   Mock the dependencies and verify interactions via these mocks.
5. Write a minimal implementation to pass the test.
6. If any other tests break, fix them. **Here, you enter
   a recursion, starting at step 1 with a broken behaviour unit**.
7. Refactor. Remove duplication in application and tests code.
   Apply Clean/Hexagonal architecture principles when necessary.

Let's walk through these steps by implementing the original
"Vote for an article" use case from scratch.
I **will not** include implementation code here, just the tests code.
That's because the implementation stays the same, but the tests
are quite different.

Use case: Vote for an article
=============================

Let's recap the requirements for this use case:

1. Every article has a rating.
2. Users can change an article's rating by either
   "upvoting" or "downvoting" it.
3. To vote on an article, a user's karma (their user rating)
   needs to be higher than 5
4. A user can only vote on each article once.

This translates into the following user story:

.. code-block:: gherkin

   Given A registered user
         who can vote on articles.
   When they vote on an article.
   Then the article's rating changes to reflect their vote.


1. Pick a behaviour unit
------------------------

We start with a happy case scenario.
Our TODO list looks like the following:

.. code-block:: markdown

   ### TODO

   * [ ] Test that "When user successfully votes for an article,
         the system responds with HTTP CREATED status and the vote details".
   * [ ] Implement the view which handles voting for articles.

2. Write a test for its API
---------------------------

.. code-block:: python

   def test_when_user__successfully_votes_for_existing_article__system_returns_http_created_with_vote_details():
       response = post_article_vote(
           article_id='3f577757-0000-0000-0000-000000000000',
           user_id='9af8961e-0000-0000-0000-000000000000',
           vote='DOWN'
       )

       assert response.status_code == HTTPStatus.CREATED
       assert response.data == {
           'article_id': '3f577757-0000-0000-0000-000000000000',
           'user_id': '9af8961e-0000-0000-0000-000000000000',
           'vote': 'DOWN'
       }

Here ``post_article_vote()`` is a helper function which invokes the view via
``APIRequestFactory``. This keeps the tests fast and limits the context to
the strictly necessary pieces.

We run the test and it predictably fails.

3. Write a minimal implementation to pass the test
--------------------------------------------------

The first round implementation which passes this test is amazingly simple:
the view just echoes the posted data.

.. figure:: {static}api-sociable-test-echo.svg
   :align: center
   :alt: Echo HTTP request payload in response.
   :width: 100%

   The minimal implementation which passes the test - echoing
   POST payload back.

Is that it?
Does the API interaction fully describes the system behaviour?
Not really, because this behaviour is not pure, i.e. it has side effects,
and we need to store the vote somewhere.


4. Write a test to verify downstream interaction
------------------------------------------------

Mocking Django model persistence
................................

.. code-block:: markdown

   ### TODO

   * [ ] Test that "When user successfully votes for an article,
         the system persists the vote"
   * [ ] Implement persisting the vote.
   * [X] Test that "When user successfully votes for an article,
         the system responds with HTTP CREATED status and the vote details".
   * [X] Implement the view which handles voting for articles

We're using a database for storage, and Django provides out-of-the box tools
to run tests with a database backend.
You could use an in-memory SQLite, spin up a heavier DB in a Docker container,
or even use a shared database (oh the horror!).
But in my book, all these methods are rather integration tests, than unit tests,
because you are not really testing the application in isolation anymore.
The same applies to other integrations like message queues, event busses,
downstream services, file operations etc.

What we can do though, is mock and spy on the persistence mechanisms that
are furthest to the right (from the application perspective) or at the very top
(from Django's perspective).
For instance, we can mock a model's ``save()`` method and spy on it.
We can even create a pytest fixture like this:

.. code-block:: python

   @pytest.fixture
   def mock_persisting_article_vote():
       with patch.object(ArticleVoteEntity, 'save', autospec=True) as mock:
           def _mock_persisting_article_vote():
               return mock
       yield _mock_persisting_article_vote

Now we can spy on the ``save()`` method calls and verify the instance details
passed as ``self`` argument.
But let's write a test first!

.. code-block:: python

   def test_when_user__successfully_votes_for_existing_article__system_persists_the_vote_in_the_database(
       mock_persisting_article_vote,
       post_article_vote
   ):
       spy = mock_persisting_article_vote()

       post_article_vote(
           article_id='3f577757-0000-0000-0000-000000000000',
           user_id='9af8961e-0000-0000-0000-000000000000',
           vote='down'
       )

       # use the captured ``self`` value from ArticleVoteEntity().save()
       entity = spy.call_args[0][0]
       assert entity.article_id == UUID('3f577757-0000-0000-0000-000000000000')
       assert entity.user_id == UUID('9af8961e-0000-0000-0000-000000000000')
       assert entity.vote == 'down'

.. figure:: {static}mock-assert.svg
   :align: center
   :alt: Substitute Django database persistence mechanism with a mock.
   :width: 100%

   Substituting Django database persistence mechanism with a mock in a unit test.

5. Write a minimal implementation to pass the test
---------------------------------------------------

The implementation for this can be also naive - we can create and save
an ``ArticleVoteEntity`` from the HTTP POST data.
A simple and well-known Django Rest Framework flow.


7. Refactor
-----------

Mocks are for humans, not machines!
...................................

I personally find ``spy.call_args[0][0]`` very ugly and non-intuitive.
The fact that there is a comment explaining *what the line does* is already
a code smell. How about writing a custom spy object which stores the saved
entity, so that we can get the captured entity via self-explanatory

.. code-block:: python

   def test_when_user__successfully_votes_for_existing_article__system_persists_the_vote_in_the_database(...):
       ...
       entity = spy.saved_article_voted_entity
       assert entity.vote == 'down'
       ...


   class SaveArticleVoteEntitySpy:
       saved_article_voted_entity: Optional[ArticleVoteEntity] = None

       def save_article_vote_entity_mock(self, entity, *_args, **_kwargs):
           self.saved_article_voted_entity = entity


   @pytest.fixture
   def mock_persisting_article_vote():
       spy = SaveArticleVoteEntitySpy()

       with patch.object(ArticleVoteEntity, 'save', autospec=True) as save_mock:
           def _mock_persisting_article_vote() -> SaveArticleVoteEntitySpy:
               save_mock.side_effect = spy.save_article_vote_entity_mock
               return spy
           yield _mock_persisting_article_vote



Remove duplication in tests
...........................

You have probably noticed that the API response and Dependencies interaction
tests have the similar *Given* and *When* or *Arrange* and *Act* parts.
As a matter of fact, they **should** have identical parts because
we're testing the same behaviour, just from different ends!

Let's not repeat ourselves.
One way is to group the behaviour tests in a single class and
extract the *Arrange* and *Act* parts into their own fixtures
and methods. Now, this might be an overkill for a small setup, but here
is what I got in the end (`spoiler alert! <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog4/tests/test_myapp/application/test_api.py>`_):

.. code-block:: python

   class TestWhenUserSuccessfullyVotesForExistingArticle:
       @pytest.fixture(autouse=True)
       def arrange(
           self,
           given_a_user_who_can_vote,
           given_no_existing_article_votes,
           mock_persisting_article_vote,
           post_article_vote
       ):
           given_a_user_who_can_vote(
               UUID('9af8961e-0000-0000-0000-000000000000')
           )
           given_no_existing_article_votes()
           self.persisting_article_vote_spy = mock_persisting_article_vote()
           self.post_article_vote = post_article_vote

       def act(self) -> Response:
           return self.post_article_vote(
               article_id='3f577757-0000-0000-0000-000000000000',
               user_id='9af8961e-0000-0000-0000-000000000000',
               vote='down'
           )

       def test_system_returns_http_created_with_vote_details(self):
           response = self.act()
           assert response.status_code == HTTPStatus.CREATED
           assert response.data == {
               'article_id': '3f577757-0000-0000-0000-000000000000',
               'user_id': '9af8961e-0000-0000-0000-000000000000',
               'vote': 'DOWN'
           }

       def test_system_persists_the_vote_in_the_database(self):
           self.act()
           entity = self.persisting_article_vote_spy.saved_article_voted_entity
           assert entity.article_id == UUID('3f577757-0000-0000-0000-000000000000')
           assert entity.user_id == UUID('9af8961e-0000-0000-0000-000000000000')
           assert entity.vote == 'down'



So far, so good, nothing is failing!
Our next step, however, is going to shake things up a little bit.


Use case: Only existing user can vote for an article
====================================================

1. Pick a behaviour unit
------------------------

.. code-block:: markdown

   ### TODO

   * [ ] Test that only existing user can vote for an article.

First, let's define an existing user as a record in the database.
Second, our current tests already cast a vote by the given ``user_id``.
So, no matter how we tweak the "Assert" and "Arrange" (or
"Then" and "When") parts of the test, it will pass as long as we keep
those parts aligned.  We need a new test that *will* break,
and guide implementation further:

.. code-block:: markdown

   ### TODO

   * [ ] **Test that a non-existing user can't vote for an article.**
   * [ ] Test that only an existing user can vote for an article.


2. Write a test for its API
---------------------------

Our system responds with ``HTTP NOT FOUND`` in this case:

.. code-block:: python

   def test_when_voting__as_non_existing_user__system_returns_http_not_found_with_error_details(
       given_no_existing_users,
       post_article_vote
   ):
       given_no_existing_users()

       response = post_article_vote(
           user_id='a3853333-0000-0000-0000-000000000000'
       )

       assert response.status_code == HTTPStatus.NOT_FOUND
       assert response.data == {
           'detail': "User 'a3853333-0000-0000-0000-000000000000' not found",
           'status': 404,
           'title': 'Error'
       }

This looks simple - we setup a system that doesn't have any users and then
try to vote. The system should respond with an error.
``given_no_existing_user()`` is a stub which returns no users when you try
to search for them. In Django terms, that's a temporary ``ObjectManager``,
with the necessary methods' stubs:

.. code-block:: python

   class VotingUserEntityEmptyObjectManagerMock:
       def get(self, *_args, **_kwargs) -> VotingUserEntity:
           raise VotingUserEntity.DoesNotExist()

The fixture substitutes the object manager for a single test run:

.. code-block:: python

   @pytest.fixture
   def given_no_existing_users():
       original_voting_user_entity_manager = VotingUserEntity.objects

       def _given_no_existing_user():
           VotingUserEntity.objects = VotingUserEntityObjectManagerMock()
       yield _given_no_existing_user

       VotingUserEntity.objects = original_voting_user_entity_manager


If we run the test, it fails because the logic implementation is missing.
To turn the test green, we need to query the database, check whether
a user exists, and return ``HTTP 404`` otherwise.
Once that is ready, the last test passes,
however, **the first two tests fail** when trying to access the database
since there is no way to set up existing users yet:

.. code-block:: none

   Unexpected error occurred: Database access not allowed,
   use the "django_db" mark, or the "db" or "transactional_db" fixtures
   to enable it.



.. important::

   Think about it for a sec! How would you mock an existing user?


6. Fix failing tests
--------------------

Mocking existing users
......................

We can mock existing users the same way we mocked "no existing users" - by
mocking the objects manager. First, we'll enable the manager to hold аnd return
a ``VotingUserEntity`` stub:

.. code-block:: python

   class VotingUserEntityObjectManagerMock:
       stub: VotingUserEntity | None = None

       def __init__(self, stub: VotingUserEntity):
           super().__init__()
           self.stub = stub

       def get(self, *_args, **_kwargs) -> VotingUserEntity:
           if self.stub is None:
               raise VotingUserEntity.DoesNotExist()
           return self.stub

You can probably see where this is going, right?
All we need to add is a fixture builder:

.. code-block:: python

   @pytest.fixture
   def given_voting_user():
       original_voting_user_entity_manager = VotingUserEntity.objects

       def _given_voting_user(
           user_id: UUID = uuid4(),
           karma: int = 10
       ):
           VotingUserEntity.objects = VotingUserEntityObjectManagerMock(
               VotingUserEntity(
                   user_id=user_id,
                   karma=karma
               )
           )
       yield _given_voting_user

       VotingUserEntity.objects = original_voting_user_entity_manager

7. Refactor BIG
---------------

Did you notice that we have already implemented a couple of behaviour units
inside a Django View, i.e. an API adapter? At this point we can start refactoring
the code by adding the necessary abstractions, service, and domain layers,
and moving Django model interaction code to SPI adapters.

.. note::

   This is where things get a bit controversial.
   Remember that tests are meant to guide development.
   Hence, we must drive the development of the application core
   via proper solitary and sociable tests!

We are able do these refactorings because our tests cut through
all the application layers and verify the behavior on its edges.


The price to pay
================

The lightweight integration tests let us quickly test application as a whole,
using mocks only at the system edges.
However, these mocks can become quite sophisticated because a single
use case triggered at the API often results in many downstream
interactions.
For example, imagine a scenario where the application returns
HTTP 409 - Conflict, when someone votes for an article a second time.
We'll need to mock ``User.objects`` (a Django DB model ObjectManager)
to provide an existing user, as well as provide an existing article
via a mocked ``Article.objects`` manager.

At some point, the mocks can become *too* sophisticated and create a mess
of their own.
That's when *real* integration testing alternatives like in-memory SQLite,
or even `Testcontainers <https://testcontainers.com/>`__ start making more sense.
We may loose the rapid feedback of unit tests, but save ourselves a lot of
time spent on maintenance of messy test doubles.

Conclusion
==========

Solitary unit tests are excellent for developing individual components in isolation.
Sociable unit tests are a classical approach to testing pieces together, mocking
the complicated dependencies, for example, those which cross the I/O boundary.
Both solitary and sociable unit tests are my tools of choice
for test-driven development.

Lightweight integration tests ensures that all components
work together correctly as a complete application,
while preserving the speed and flexibility of unit tests.
However, we need to invest significantly in edge mocks to emulate rightmost
interactions. Moreover, these tests primarily drive the implementation of
application edges - the adapters.

Lightweight integration tests are a good alternative
to either missing integration tests or integration tests which require
an equally complicated setup.
They can be quite useful when refactoring a legacy system, that doesn't have
any tests. We can capture the interaction on the edges and ensure that
it doesn't change during development.


Acknowledgements
================

Once again, `Jarkko "jmp" Piiroinen <https://github.com/jmp>`_
nudged me to dive deeper into the subject and challenge
my own understanding of the subject.
I'm very grateful for your input, Jarkko!
