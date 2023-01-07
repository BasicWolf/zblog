Hexagonal architecture and Python - Part III: Persistence, Transactions, Exceptions and The Final Assembly
##########################################################################################################

:slug: hexarch_di_python_part_3
:category: Articles
:tags: architecture, DDD, dependency injection, Django, hexagonal architecture, programming, python,
:date: 2022-12-31 17:19
:summary: .. image:: {static}hexagonal-python-3.jpg
             :align: center
             :alt: Python logo in a hexagon with Roman III literal
             :target: {filename}2022_12_31_hexarch_di_python_part_3.rst

          Welcome to the third part of the article series, which cover principles of
          Hexagonal architecture, Dependency Injection, Domain-Driven Design and applies
          these all to Python and Django application design.

.. _hexarch_di_python_part_3:

.. image:: {static}hexagonal-python-3.jpg
   :align: center
   :alt: Python logo in a hexagon with Roman III literal
   :target: {filename}2022_12_31_hexarch_di_python_part_3.rst

In
`Part II <{filename}../2022_09_18_hexarch_di_python_part_2/2022_09_18_hexarch_di_python_part_2.rst>`__
we discussed the Hexagonal architecture of ports and adapters,
the role of the Domain layer and its influence on API and database layers.
We exposed the application to the outer world via the HTTP API port.

In Part III we are going to
put all the application pieces together.
But before that,
we have to connect the application to the database,
research Django transactions in unit tests and
set up exception handling on the HTTP API level.


The repository
==============

We love Django for many things, but most of them all - is the fantastic ORM.
Django ORM abstracts the underlying database so gracefully that
swapping one database engine to another is just a matter of updating the application
configuration.
But what if there is another data storage not supported by Django?
What if the data storage is a web service?

This problem is commonly solved via the
`Repository design pattern <https://learn.microsoft.com/en-us/previous-versions/msp-n-p/ff649690(v=pandp.10)>`__.
A repository separates the logic of communicating with the database
from the rest of the application. In terms of Hexagonal architecture, a
repository is an SPI adapter that handles commands and queries from one
or more related ports.

Code-wise, the ``VotingUserRepository``
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/application/adapter/spi/persistence/repository/voting_user_repository.py#L21>`__
is a class that implements
the ``FindVotingUserPort``
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/application/port/spi/find_voting_user_port.py#L8>`__
and the ``SaveVotingUserPort``
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/application/port/spi/save_voting_user_port.py#L6>`__
ports:

.. code-block:: python

   # /src/myapp/application/adapter/spi/persistence/repository/voting_user_repository.py

   class VotingUserRepository(
       FindVotingUserPort,
       SaveVotingUserPort
   ):
       def find_voting_user(self, article_id: ArticleId, user_id: UserId) -> VotingUser:
           ...
           return VotingUser(...)

       def save_voting_user(self, voting_user: VotingUser) -> VotingUser:
           ...
           return VotingUser(...)

Strictly speaking, there is no need to use the Repository pattern here.
We have already decoupled the application from the data stores via SPI ports.
However, a repository is a convenient way of putting related adapter implementations
in one place.
The ``VotingUserRepository`` provides database-backed adapters for both
``FindVotingUserPort`` and ``SaveVotingUserPort`` SPI ports.
It communicates with the database through Django ORM:


.. image:: {static}the-voting-user-repository.svg
   :align: center
   :alt: A diagram which shows the data flow between VotingUserRepository,
         Django ORM and a Database.
   :width: 100%



From domain models to database entities
---------------------------------------


The ``VotingUserRepository`` has to map the ``VotingUser`` domain model to
data model(s) when saving to - and vice versa, when reading from the database.
The ``VotingUser`` model holds three pieces of information,
which eventually influence the database design
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/application/domain/model/voting_user.py#L20>`__:

.. code-block:: python

   # /src/myapp/application/domain/model/voting_user.py

   class VotingUser:
       id: UserId
       karma: Karma
       votes_for_articles: list[ArticleVote]


A modern relational database with native JSON support can store such
an object in a single table row. Django natively supports JSON fields
and provides unbelievable
`JSON querying capabilities <https://docs.djangoproject.com/en/4.1/topics/db/queries/#querying-jsonfield>`__.

A more traditional way is to store ``ArticleVotes`` and ``VotingUsers`` in separate
tables with an explicit relationship between them:

.. uml::
   :class: align-center

   @startuml
   left to right direction
   skinparam roundcorner 5
   skinparam linetype ortho
   skinparam shadowing false
   skinparam handwritten false
   skinparam class {
       BackgroundColor white
       ArrowColor #2688d4
       BorderColor #2688d4
   }

   !define primary_key(x) <b><color:#b8861b><&key></color> x</b>
   !define foreign_key(x) <color:#aaaaaa><&key></color> x
   !define column(x) <color:#efefef><&media-record></color> x
   !define table(x) entity x << (T, white) >>
   !define constraint(x) <color:orange><&shield></color> x

   table( voting_user ) {
      primary_key( id ): UUID
      --
      column( karma ): INTEGER
   }
   table( article_vote ) {
      primary_key( id ): UUID
      --
      foreign_key( user_id ): UUID
      foreign_key( article_id ): UUID
      column( vote ): TEXT(4)
      ==
      constraint( unique(user_id, article_id) )
   }

   voting_user --{ article_vote
   @enduml

|

.. note::

   Although I drew ``article_vote.user_id`` and ``article_vote.article_id`` as
   **foreign keys**, this is not reflected in the example project code.
   There is some hidden complexity here, like -
   if a user gets deleted, should the article votes stay? Or should they remain
   intact if an article gets deleted? If yes - how should we preserve the data?
   I hope you would indulge me this simplification and leave the
   proper foreign key relationships and domain-specific deletion handling for
   another time.


I bet you already picture how to express these tables as Django models.
Here is a tricky question: where should we put them?
It's not hard to answer if you remember the structure of HTTP API adapters.
Let's do something similar for our persistence SPI adapter:

.. code-block:: text

   myapp/application/adapter/spi/
       persistence/
           entity/
               article_vote_entity.py     # Django model here
               voting_user_entity.py      # and here
           repository/
               voting_user_repository.py
           exceptions/
               ...

Here is another unorthodox move: I called Django models "*Entities*".
That is - to avoid confusion between *domain models* and *Django models*.
There is no other hidden meaning of "Entity" in this case.

Here is the ``ArticleVoteEntity``
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/application/adapter/spi/persistence/entity/article_vote_entity.py#L8>`__:

.. code-block:: python

   # /src/myapp/application/adapter/spi/persistence/entity/article_vote_entity.py

   class ArticleVoteEntity(models.Model):
       VOTE_UP = 'up'
       VOTE_DOWN = 'down'

       VOTES_CHOICES = [
           (VOTE_UP, 'UP'),
           (VOTE_DOWN, 'DOWN')
       ]

       id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
       user_id = models.UUIDField()
       article_id = models.UUIDField()
       vote = models.CharField(max_length=4, choices=VOTES_CHOICES)

       class Meta:
           unique_together = [['user_id', 'article_id']]
           db_table = 'article_vote'

The ``VotingUserEntity`` is simpler
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/application/adapter/spi/persistence/entity/voting_user_entity.py>`__
:

.. code-block:: python

   # /src/myapp/application/adapter/spi/persistence/entity/voting_user_entity.py

   class VotingUserEntity(models.Model):
       user_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
       karma = models.IntegerField()

       class Meta:
           db_table = 'voting_user'

The entity definitions are lean and have no methods in them.
All that is required - is to map data from Python to database and back.
And Django flawlessly does that.


Inside the repository
---------------------

Once you've seen the entities (i.e. Django models), things get very predictable.
The repository implements two SPI ports - one to get a ``VotingUser`` from the
database, another to persist a ``VotingUser`` to the database.
The repository takes care of transforming the domain model to Django entities
and calling the required Django ORM methods. The repository then transforms
the result back to the domain model:

.. image:: {static}voting-user-to-database.svg
   :align: center
   :alt: A diagram which shows how VotingUser domain model is persisted to
         a database through Django ORM mechanism.
   :width: 100%

The implementation fits just in few lines after hiding Django ORM boilerplate in
private methods
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/application/adapter/spi/persistence/repository/voting_user_repository.py#L25>`__:

.. code-block:: python

   # /src/myapp/application/adapter/spi/persistence/repository/voting_user_repository.py

   def find_voting_user(self, article_id: ArticleId, user_id: UserId) -> VotingUser:
       voting_user_entity = self._get_voting_user_entity(user_id)
       votes_for_articles = self._get_votes_for_articles(article_id, user_id)

       return VotingUser(
           user_id,
           Karma(voting_user_entity.karma),
           votes_for_articles
       )

Remember that I put no explicit ``ForeignKey`` relationships here, so we
have to load the votes manually. A user is saved in the same fashion
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/application/adapter/spi/persistence/repository/voting_user_repository.py#L57>`__:

.. code-block:: python

   # /src/myapp/application/adapter/spi/persistence/repository/voting_user_repository.py

   def save_voting_user(self, voting_user: VotingUser) -> VotingUser:
       saved_voting_user_entity = self._save_voting_user(voting_user)
       saved_article_vote_entities = self._save_votes_for_articles(
           voting_user.votes_for_articles
       )

       return self._voting_user_entity_to_domain_model(
           saved_voting_user_entity,
           saved_article_vote_entities
       )




Perhaps you are wondering: **why map a** ``VotingUserEntity`` **back to a**
``VotingUser`` **domain model if we already pass it as an argument?**
The data passed in an INSERT INTO statement may run through numerous
transformations before it reaches the data storage.
The well-known case is an "auto-incremental" integer primary key
generated via ``BEFORE INSERT`` triggers.
So, it is paramount to return a domain model that resembles
the updated database state, not what we pass to the routine.

Transactions management
=======================

A common way to handle database transactions in Django - is to wrap each HTTP
request in a transaction.
This works for simple cases. But what does it mean in terms of
Hexagonal architecture? In
`Part II <{filename}../2022_09_18_hexarch_di_python_part_2/2022_09_18_hexarch_di_python_part_2.rst>`__
we created an HTTP API adapter, which invokes the ``VoteForArticleUseCase``
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/application/port/api/vote_for_article_use_case.py#L9>`__.

But there could be many other adapters - a command line adapter,
a message bus adapter, an RPC adapter etc.
We can't trust all those adapters to wrap a use case in a transaction.
So, the burden of defining transaction boundaries is shifted to
a use case implementation - an application service.
An application service places the database write operations into a single transaction.
The operations then roll back if one of them fails.

Transactions in Django
----------------------

We know that an application service
vows to be agnostic of SPI adapters' implementation details.
But wrapping SPI calls in transaction breaks this vow.
Correction: wrapping SPI calls in a transaction *using Django routines* breaks
this vow.
Django's `transaction.atomic <https://docs.djangoproject.com/en/4.1/topics/db/transactions/#controlling-transactions-explicitly>`_
is the unambiguous way to wrap a code block in a transaction.
It is used either as a decorator or a context manager.
But the problem is that Python decorators and context managers are runtime
constructs. Internally ``transaction.atomic`` operates on database connection
object. While we certainly need a database connection at a run time, we
don't need one for *unit* testing.
This means that the following perfectly valid production code

.. code-block:: python

   from django.db import transaction

   class ArticleRatingService(VoteForArticleUseCase):
       @transaction.atomic
       def vote_for_article(self, command):
           ...

fails in a unit test (pytest) with ``RuntimeError("Database access not allowed...")`` exception, unless a database connection is established.
The exception suggest marking the test with **@pytest.mark.django_db** - but
this turns a *unit* test into an *integration* test!

With all the "batteries included", Django doesn't include one for this case.
My version of such a battery is ``@transactional`` decorator, which
wraps a callable in a transaction for production, but skips it when running tests
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/application/util/transactional.py#L11>`__.

.. warning::

   **Code smell detected**.
   A routine in a production code made solely for the sake of testing is
   a sign of a bad design. However, such hack is necessary to push a Django
   application out of the framework box.

SPI adapters exceptions
=======================

Traditionally handling exceptions in Django views boils down to wrapping a block of
code in ``try..except`` and returning an error-indicating result:

.. code-block:: python

   def get_user_name(request, user_id):
       try:
           user = User.objects.get(user_id=user_id)
           return HttpResponse(user.name)
       except User.DoesNotExist:
           return HttpResponseNotFound("User not found :(")

But how does an API adapter handles an exception raised by an SPI adapter?
The dependencies directions principle in Hexagonal Architecture reminds us that
API adapters should not be aware of SPI **adapters**' innards.

.. image:: {static}hexagonal-architecture-dependencies.svg
   :align: center
   :alt: Hexagonal Architecture layers, from top to bottom: Adapters, Ports,
         Application Services, Domain
   :width: 35%


Instead, they are aware of interfaces exposed by SPI **ports**.
An SPI **port** is not necessarily a bare interface.
It includes type definitions, exceptions and other constructs that make an SPI
port a whole. Our SPI port includes such an exception
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/application/adapter/spi/persistence/exceptions/voting_user_not_found.py>`__:

.. code-block:: python

   # /src/myapp/application/adapter/spi/persistence/exceptions/voting_user_not_found.py

   class VotingUserNotFound(RuntimeError):
       def __init__(self, user_id: UserId):
           super().__init__(f"User '{user_id}' not found")

The SPI adapter catches the downstream ``User.DoesNotExist`` exception
and re-throws it upstream in form of ``VotingUserNotfound``
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/application/adapter/spi/persistence/repository/voting_user_repository.py#L39>`__:

.. code-block:: python

   # /src/myapp/application/adapter/spi/persistence/repository/voting_user_repository.py

   def _get_voting_user_entity(self, user_id: UserId) -> VotingUserEntity:
       try:
           return VotingUserEntity.objects.get(user_id=user_id)
       except VotingUserEntity.DoesNotExist as e:
           raise VotingUserNotFound(user_id) from e


Exception handler
-----------------

Now that we know which exception to catch in the HTTP API adapter,
let's discuss ways to handle it.
The most obvious way is to wrap the body of ``ArticleVoteView.post()`` in
``try..except`` statement.
That works fine for a small number of exceptions, but in a larger
application with lots of exceptions of a similar origin, a common mechanism might
be preferable.
For example, an "Entity Not Found" exception can be expressed as the ``HTTP 404``
response for any kind of entity.
Luckily for us, Django Rest Framework provides a common exception-handling mechanism.
You can define a
`custom exception handler <https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling>`_
function and set ``REST_FRAMEWORK.EXCEPTION_HANDLER`` settings value.

If a simple form, the handler catches SPI exceptions and converts them to an HTTP
response
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/application/adapter/api/http/exceptions_handler.py>`__:

.. code-block:: python

   # /src/myapp/application/adapter/api/http/exceptions_handler.py

   def exceptions_handler(exc, context):
       ...
       if isinstance(exc, VotingUserNotFound):
           return Response({
               'title': "Error",
               'detail': str(exc),
               'status': HTTPStatus.BAD_REQUEST
           })

The Final Assembly
==================

All the components of the application - the domain model, application services,
API and SPI adapters are ready. All that is left - is to put them together.
We are going to use a small dependencies or
`Inversion of Control <https://www.martinfowler.com/articles/injection.html>`_
container that creates all the components instances and wires them into a
complete application:

.. image:: {static}ioc-container.svg
   :align: center
   :alt: A diagram which shows how Django passes control flow to the IoC
         Container.
   :width: 80%

The container commences by instantiating ``VotingUserRepository``.
It is the sole component with no dependencies.
Next, the container instantiates the components that depend
on the already available components instances, i.e. ``ArticleRatingservice``
that solely depends upon ``VotingUserRepository``.
It continues recursively assembling components until the dependency tree is
fully populated
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/dependencies_container.py#L10>`__:

.. code-block:: python

   # /src/myapp/dependencies_container.py

   def build_production_dependencies_container() -> Dict[str, Any]:
       voting_user_repository = VotingUserRepository()

       article_rating_service = ArticleRatingService(
           find_voting_user_port=voting_user_repository,
           save_voting_user_port=voting_user_repository
       )

       article_vote_django_view = ArticleVoteView.as_view(
           vote_for_article_use_case=article_rating_service
       )

       return {
           'article_vote_django_view': article_vote_django_view
       }


Notice that container only exposes a single entry point: the HTTP view, i.e.
the API adapter.

Configuration
-------------

Where and when should we build the container? Consider this: the container
creates and wires the components together. We can use different components
for different environments - e.g. have a ``VotingUserExcelRepository``.
So, the container **configures** the application.
And Django applications have a well-known place for configurations - the
`AppConfig <https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.AppConfig>`_ class
and the ``AppConfig.ready()`` method:

.. code-block:: python

   # /src/myapp/apps.py

   class MyAppConfig(AppConfig):
       name = 'myapp'
       container: Dict[str, Any]

       def ready(self) -> None:
           from myapp.dependencies_container import build_production_dependencies_container
           self.container = build_production_dependencies_container()

URLs
----

The application configuration registry is populated *before* Django sets up
the URLs. It allows to get the application configuration from the registry
and bind the view to a URL
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/urls.py>`__:

.. code-block:: python

   # /src/myapp/urls.py

   app_config = django_apps.get_containing_app_config('myapp')
   article_vote_django_view = app_config.container['article_vote_django_view']

   urlpatterns = [
       path('article_vote', article_vote_django_view)
   ]



Django models
-------------

Django expects to find models in application's ``models.py`` file.
Since we declared the entities deep down in SPI adapters, they have to be
imported manually here
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/src/myapp/models.py>`__:

.. code-block:: python

   # /src/myapp/models.py

   from myapp.application.adapter.spi.persistence.entity.article_vote_entity import (
       ArticleVoteEntity
   )
   from myapp.application.adapter.spi.persistence.entity.voting_user_entity import (
       VotingUserEntity
   )


Testing
-------

**The Final Assembly** is a slightly misleading term. There is no need to wait
for all the components to be available to assemble a production-level
application container.
On the surface, a container exposes an API entry point,
backed either by a production-grade component or a dummy.

So, the dependencies container should not be the last but one of the
first items on the list when building an application following
Hexagonal architecture principles.
You can add the components to the container as they get ready and test every time
how they fit together
`[source] <https://github.com/BasicWolf/hexagonal-architecture-django/blob/blog3/tests/test_myapp/test_dependencies_container.py>`__:

.. code-block:: python

   # tests/test_myapp/test_dependencies_container.py

   def test_build_production_ioc_container():
       build_production_dependencies_container()

At the same time, a simple **smoke test** can make a vote by a non-existing
user and expect a response with HTTP 404 - Not Found status back:

.. code-block:: shell

   curl http://localhost:8000/api/article_vote \
   --header "Content-Type: application/json" \
   --request POST \
   --data '{
      "user_id": "efed6f83-49ee-4cbc-bdbd-2b92bf428f2b",
      "article_id": "60ccea0c-0bf2-4726-8ac7-324fa03a74cd",
      "vote": "UP"
    }'

   >
   {
       "title":"Error",
       "detail":"User 'efed6f83-49ee-4cbc-bdbd-2b92bf428f2b' not found",
       "status":404
   }


Bear in mind that the job of a smoke test is to verify whether the application
works. An ideal smoke test touches all the application layers
without affecting its state. Voting by a non-existing user cuts through all the
application layers, down to the database and returns the expected error result.

This test can also run against an application-in-development with
a dummy HTTP or SPI (database) adapters.
Replacing a dummy adapter with a real one should not require any
modifications to the test.

Final thoughts
==============

It took me almost two years to complete this article series. The example code
lived through two major rewrites and has been continuously evolving.
I am satisfied with the output and the outcome of this work.
It helped me to understand Hexagonal Architecture and dive deeper into DDD.
I hope it makes an inspiring impact on fellow Pythonistas!

Acknowledgments
===============

Traditionally, `Jere "Urokhtor" Teittinen <https://jereteittinen.info>`__
gave priceless feedback on the draft, for which I am very grateful!
