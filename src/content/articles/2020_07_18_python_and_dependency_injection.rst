Python and dependency injection
===============================

:slug: python_and_dependency_injection
:categories: Articles
:tags: programming, python, dependency injection
:date: 2020-07-18 12:00
:status: draft

Dependencies and abstractions
-----------------------------

Dependencies are everywhere. Our mornings
often start with the least pleasing dependency
- an alarm clock. The following dependencies
are running water in a bathroom and electricity
to brew hot coffee and have a fresh breakfast.
Imagine the galaxy of dependencies required
to pump that water and electricity into
a house. Water and power plants, all the equipment
and all the plumbing and power lines!

Our world runs on dependencies. However, is it a concrete
dependency or just its abstract capabilities that we depend upon?

Imagine that you have to make a phone call over GSM phone network.
Does it matter, whether you use an IPhone, an Android
device, or even a good-old stationary phone?

You are probably reading this article from
a screen - be it a monitor, a mobile device,
or a e-Ink display. It doesn't really matter which one.

It is a wonderful Saturday evening and you are
on a geeks meetup. "Can someone please pass me a beer?"
Someone passes you a beer and you thank them. It could
be anyone, your best friend, or someone you've
met for the first time. It doesn't matter since
you got the beer.

Tadaaam! You've just rediscovered the **Dependency Inversion Principle**.
Robert Martin defined the Dependency Inversion Principle in two statements: [2]_

1. High-level modules should not depend on low-level modules. Both should depend on abstractions.
2. Abstractions should not depend on details. Details should depend upon abstractions.

Back to the beer example: you, a lazy and thirsty Python developer (**high-level module**)
does not depend on a concrete person (**low-level module**) in the room.
All you want is to get a beer (**abstract action**). You also do not depend upon **details**:
it could be a bottle, a can, a pint glass - your friend would figure it out.
But he knows, that you won't be happy with a 2 litre plastic bottle:
it is too thick to be comfortably held in one hand (**detail depending upon abstraction**).

Dependencies through the eye of the Python
------------------------------------------

In terms of software development,
*a dependency is an object, that another object requires.* [1]_

Let's have a look at an example function which sends an alert
via a messaging bus:

.. code-block:: python

  from message_bus_library import MessageBus, MemoryMessageBus, Priority

  message_bus: MessageBus = MemoryMessageBus()

  def send_alert(message: str):
      message_bus.send(
          topic='alert',
          priority=Priority.HIGHEST,
          message=message
      )

Here ``send_alert()`` function depends on ``message_bus`` object
and its ``.send()`` method.
In other words, ``message_bus`` is a **dependency** of  ``send_alert()``.


Dependency Injection
--------------------

Using a global variable as a dependency is simple and easy to start with,
but it quickly becomes a maintenance nightmare.
Consider the kind of "dark magic" required to write a unit test
for ``send_alert`` - the module has to be monkey patched in order
to replace ``message_bus`` with a test double.

Another way is to pass the dependency as a function
argument:

.. code-block:: python

  from message_bus_library import MessageBus, Priority

  def send_alert(message_bus: MessageBus, message: str):
      message_bus.send(
          topic='alert',
          priority=Priority.HIGHEST,
          message=message
      )

This small change brings an immediate improvement to the code.
There are no more magic global variables, and what is even
more important - **it is obvious that send_alert()
depends on a MessageBus object**.
Testing ``send_alert()`` is also simple, since
a test double, such as a mocked ``MessageBus`` instance
is explicitly passed to the function.
The huge downside is that ``message_bus`` has to be
passed to every ``send_alert()`` call.

There are different ways to tackle this:

**Functional** - create a closure (a partial function)
which wraps ``send_alert`` and supplies its first
argument. For example:

.. code-block:: python
   :linenos:

   from functools import partial
   from message_bus_library import MessageBus, get_message_bus

   def _send_alert(message_bus: MessageBus, message: str):
       ...

   send_alert = partial(_send_alert, message_bus=get_message_bus())

Do you see the trap? ``send_alert`` is a closure which is initialized
"right here, right now" - when Python processes line #7.
This means that the ``message_bus`` argument has to be resolved
*before* application code is fully loaded.
To solve this problem ``send_alert`` initialization must be delayed
until its dependencies are ready.

**Object-Oriented** - put the ``send_alert`` method in a class
and store the dependency to the class field via ``__init__()``:

.. code-block:: python

  class AlertDispatcher:
      _message_bus: MessageBus

      def __init__(self, message_bus: MessageBus):
          self._message_bus = message_bus

      def send(message: str):
          self._message_bus.send(
              topic='alert',
              priority=Priority.HIGHEST,
              message=message
          )

This eliminates the initialization problem:
``AlertDispatcher`` can be instantiated with the required dependency
after Python fully loads the program files to memory.

Now that dispatching alerts is handled by a class,
putting a message bus and an alert dispatcher together is simple:

.. code-block:: python

   ...
   rabbit_message_bus = RabbitMQBus()
   alert_dispatcher =  AlertDispatcher(rabbit_message_bus)
   ...
   if reactor_meltdown_detected:
       alert_dispatcher.send('Reactor is no more!')


Notice how ``AlertDispatcher`` object is constructed.
Its ``message_bus`` dependency is fulfilled by  an instance of``RabbitMQBus``.
In other words, the *dependency is injected* into an object, while the object
is being initialized (constructed).

  In software engineering, *dependency injection* (DI) is a technique in which an
  object receives other objects that it depends on.
  The receiving object is called a *client* and the passed (that is, "injected")
  object is called a *service*.
  The service is made part of the client's state. Passing the service to the client,
  rather than allowing a client to build or find the service, is the fundamental
  requirement of the pattern. [3]_


**Passing the service to the client, rather than allowing a client to build
or find the service** is the key concept of DI. In the example above
``AlertDispatcher`` doesn't look for ``message_bus``, but instead requires
``message_bus`` to be passed during initialization.


Inversion of Control Containers
-------------------------------

Dependency Injection pattern seems to solve many problems, but it
comes at a dangerously high cost. In one sentence: big bowl of
dependencies spaghetti.
Consider this: what if ``AlertDispatcher`` requires
two dependencies, and each of those requires even more?

.. code-block:: python

  class AlertDispatcher:
      def __init__(
          message_bus: MessageBus,
          alert_serializer: AlertSerializer
      )
          ...

  class MemoryMessageBus:
      def __init__(heap_memory_provider: HeapMemoryProvider)
          ...

  class AlertSerializer:
      def __init__(
          string_serializer: StringSerializer,
          binary_serializer: BinarySerializer
      ):
          ...

Imagine that one has to initialize all these dependencies manually!
Imagine that dependencies are initialized somewhere at the middle
of the running application process. Sounds terrific, doesn't it?

That's where **Inversion of Control (IoC) containers** or
**Dependency Injection frameworks** come into play.

An IoC container is an application component
(a tool, a library, a framework - pick your favourite)
which manages the dependencies life cycle.
*Inversion* means that it is the container which instantiates
the dependencies and their consumers and routes the control
flow to the consumers' methods.
This may sound a bit cryptic, but I am sure you will get the idea
in a moment.

Some IoC containers require explicit dependencies declaration,
other scan application code and structure to build the dependencies
tree automatically.

**Pytest** is probably the most famous IoC container in Python
ecosystem. Pytest

1. Scans the application for tests and fixtures.
2. Instantiates the fixtures.
3. Calls the tests (``test_*()``) functions and methods
4. Injects the instantiated fixtures into the test by matching
   test function arguments and fixture names.

Here is an example from pytest documentation:


.. code-block:: python

    # content of conftest.py
    import pytest
    import smtplib


    @pytest.fixture(scope="module")
    def smtp_connection():
        return smtplib.SMTP("smtp.gmail.com", 587, timeout=5)

The name of the fixture is ``smtp_connection`` and you can access
its result by listing the name ``smtp_connection`` as an input
parameter in any test function.

.. code-block:: python

    # content of test_module.py

    def test_ehlo(smtp_connection):
        response, msg = smtp_connection.ehlo()
        assert response == 250
        assert b"smtp.gmail.com" in msg
        assert 0  # for demo purposes

Here, ``smtp_connection`` is a *dependency*, ``test_ehlo`` is
a dependency *consumer* and pytest is an *IoC container*, which
orchestrates the execution flow.


Abstractions and dependencies
-----------------------------


Did you notice that ``AlertDispatcher`` does not depend on concrete
``MessageBus`` implementation? It could be ``MemoryMessageBus``,
``DBus``, ``RabbitMQ`` or anything else implementing the required
method - after all, Python is a dynamic language with duck typing.


``MessageBus`` could be defined as an abstract class, or a protocol:


Targeted unit testing
---------------------


Clean architecture and more
---------------------------

References
----------

.. [1] `Dependency injection in ASP.NET Core <https://docs.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-3.1>`_
.. [2] Robert Martin C. (2003), *Agile Software Development, Principles, Patterns, and Practices*. ISBN 978-0135974445.
.. [3] Dependency Injection. From Wikipedia. Retrieved on 2020.08.15. URL: https://en.wikipedia.org/wiki/Dependency_injection
