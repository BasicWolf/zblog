Domain-driven design, Hexagonal architecture of ports and adapters, Dependency injection and Python - Part I
############################################################################################################

:slug: ddd_hexarch_di_python_part_1
:categories: Articles
:tags: programming, python, hexagonal architecture, dependency injection, DDD
:date: 2021-06-11 12:00
:status: draft


Does the article title sounds like a dark magic spell?
I assure you, it is all safe, as long as you know how to treat it.
Welcome to this small series of advanced articles.
The series covers principles of Hexagonal architecture in Django application design.

Time flies awfully fast!
Two years ago I left the world of Django and found myself in the world of
Kotlin, Java and Spring Boot.
It was a genuine cultural shock.
An extensive amount of new knowledge was bombarding my brain.
Sometimes I felt so helpless, that I wanted to run back to
the beloved and bytewise familiar Python ecosystem.
Inversion of Control (IoC) was the hardest topic to digest.
Automated Dependency Injection (DI) felt like black magic,
compared to Django's direct approach.
Nonetheless, that core capability of Spring Boot framework
allowed us to design application following Hexagonal architecture rules.
While the final challenge was getting rid of the old "implement
a backlog of features" habit in place of Domain-Driven Design (DDD).

Our project rapidly grows in size and complexity.
Yet it is easy to maintain, support and develop
- thanks to the great quality of its foundation and architecture.
The code is expressive and comprehensible.
The components are easily interchangeable.
By all means this application is better than anything written
by the team members in past.

I look behind and see all the gaps in my previous experience.
The gaps which did not allow solving business problem as elegantly.
Welcome, fellow Pythonista!
This small articles series is about Hexagonal architecture and
essential topics surrounding it.

Dependency Injection
====================

Do you what is Dependency Injection (DI)?
Sure you do, even if you can't recall its explicit definition.
Let's see what are the pros and cons of this approach (if you prefer - pattern).

Imagine that we need a function which sends ALARM messages to a message bus.
The first iteration could be the following:

.. code-block:: python

   from my_cool_messaging_library import get_message_bus()

   def send_alert(message: str):
       message_bus = get_message_bus()
       message_bus.send(topic='alert', message=message)

Is there anything wrong with ``send_alert()`` function?
It depends upon ``message_bus`` object, but this dependency
is hidden from the caller.
What if you'd like to use another message bus?
How about the level of magic required to test this function?
Did I just hear ``mock.patch(...)``?
Ladies and gentlemen, this is going south, let's take another way:

.. code-block:: python

   from my_cool_messaging_library import MessageBus

   def send_alert(message_bus: MessageBus, message: str):
       message_bus.send(topic='alert', message=message)


This small change for function is a big change of paradigm.
The caller sees that ``send_alert()`` function **depends** upon
``MessageBus`` object (viva type annotations).
All implicit mocking bells and whistles are gone in favour of
explicit and clean code.
Sounds too good to be true?
Have a look:

.. code-block:: python

   def test_send_alert_sends_message_to_alert_topic()
       message_bus_mock = MessageBusMock()
       send_alert(message_bus_mock, "Hacking attempt detected!")

       assert message_bus_mock.sent_to_topic == 'alert'
       assert message_bus_mock.sent_message == "Hacking attempt detected!"

   class MessageBusMock(MessageBus):
       def send(self, topic, message):
           self.sent_to_topic = topic
           self.sent_message = message

A tempted reader raises a question: does this mean that we have to pass
an instance of ``MessageBus`` to ``send_alert()`` function on each call?
Isn't that cumbersome?

.. code-block:: python

   send_alert(get_message_bus(), "Stackoverflow is down")

Let's try solving this problem by means of OOP:

.. code-block:: python

   class AlertDispatcher:
       _message_bus: MessageBus

       def __init__(self, message_bus: MessageBus):
           self._message_bus = message_bus

       def send(message: str):
           self._message_bus.send(topic='alert', message=message)

   alert_dispatcher = AlertDispatcher(get_message_bus())
   alert_dispatcher.send("Oh no, yet another dependency!")

Now ``AlertDispatcher`` class ``depends`` on an object of type ``MessageBus``.
We **inject** this dependency when creating a ``AlertDispatcher`` object
by passing the dependency into constructor.
We have **wired** (not coupled!) the object and its dependency.

At this point the focus switches from ``message_bus`` to ``alert_dispatcher``.
This **component** may be required in different parts of the application.
Which means that there should be a global context which holds and provides
the object.
But before building such context, let's discuss the nature of components
and components wiring.


Componential Architecture
=========================

We didn't emphasize dependencies types while speaking of dependency injection.
But you might have guessed that ``MessageBus`` is just an abstraction,
an interface or what
`PEP-544 <https://www.python.org/dev/peps/pep-0544/>`_
calls a **protocol**.
Somewhere the application defines:

.. code-block:: python

   class MessageBus(typing.Protocol):
       def send(topic: str, message: str):
           pass


There is also a simple implementation of ``MessageBus`` in the project.
It stores the incoming messages in a ``list``:

.. code-block:: python

   class MemoryMessageBus(MessageBus):
       sent_messages = []

       def send(topic: str, messagge: str):
           self.sent_messages.append((str, message))

In the same manner, an abstract use case scenario is decoupled from a
business-driven implementation:

 .. code-block:: python

   # An abstract use case
   class DispatchAlertUseCase(typing.Protocol):
       def dispatch_alert(message: str):
           pass

.. code-block:: python

   # A concrete implementation in a service.
   # Note that a service may implement multiple related use cases at a time.
   class AlertDispatcherService(DispatchAlertUseCase):
       _message_bus: MessageBus

       def __init__(self, message_bus: MessageBus):
           self._message_bus = message_bus

       def dispatch_alert(message: str):
           self._message_bus.send(topic='alert', message=message)

Next, let's add a controller which accepts HTTP requests and invokes
``DispatchAlertUseCase``:

.. code-block:: python

   class ChatOpsController:
       ...
       def __init__(self, dispatch_alert_use_case: DispatchAlertUseCase):
           self._dispatch_alert_use_case = dispatch_alert_use_case

       @post('/alert)
       def alert(self, message: Message):
           self._dispatch_alert_use_case.dispatch_alert(message)
           return HTTP_ACCEPTED

Finally, let's connect all the pieces together:

.. code-block:: python

   from my_favourite_http_framework import http_server

   def main():
       message_bus = MemoryMessageBus()
       alert_dispatcher_service = AlertDispatcherService(message_bus)
       chat_opts_controller = ChatOpsController(alert_dispatcher_service)

       http_server.start()

How would a rational and clear-minded developer react to this?
"Why are you overcomplicating this?"
Which is indeed true. On the first glance, everything above fits into a short
function:

.. code-block:: python

   @post('/alert)
   def alert(message: Message):
       bus = MemoryMessageBus()
       bus.send(topic='alert', message=message)
       return HTTP_ACCEPTED

Is it short and simple? Absolutely!
Is it maintainable? Hardly.
But why?
Because the components are strongly coupled in the code.
By blending everything in a single function we tightly coupled
domain workflow and message bus implementation.
And that's half the trouble.
The worst part is that we
**melted and buried business logic in technical details**.
Don't get me wrong, such code has the right to exist.
Yet its existence in a rapidly growing application will
soon end up in maintenance hell.

Back to the componential architecture.
What are the advantages?

* Components are **isolated** and are not directly dependent.
  Instead they are **wired via abstractions**.
* Every component works in certain boundaries and **has a single responsibility**.
* This means that components are immensely testable:
  either in full isolation or in any combination using test doubles.
  There is no need to explain that testing  isolated parts of a program
  is easier compared to testing it as a whole.
  Your TDD approach improves from inaudible "well, we do tests..."
  to sonorous "tests always come first".
* It is easy to substitute components, thanks to abstract dependencies.
  In the example above ``MemoryMessageBus`` could be replaced with
  ``DbMessageBus``, ``FileMessageBus`` or anything else.
  The caller of ``message_bus.send(...)`` should not care.

Suddenly it dawns upon you:
"That sounds like... SOLID?"
It sure does.
It is almost what Uncle Bob would call a
`Clean Architecture
<https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html>`_.
I encourage you to read this article, before moving towards our end goal -
Hexagonal architecture.

Architecture is about intent
============================


One of my favourite Uncle Bob quotes on software architecture is
"Architecture is about intent".

What do you see on this screenshot?

.. image:: {static}/images/2021_06_11_hexagonal_architecture_in_python_part_1/django_project.png
   :align: center
   :alt: Typical Django project


No wonder if you recognized a "typical Django application".
Brilliant!
Can you also tell what does this application do?
If you can, my sincere congratulations - you are level 80 telepathist.
Personally I have no clue whatsoever - that is a screenshot
of a random Django application from Github.

Robert Martin develops the idea
`further <https://www.youtube.com/watch?v=WpkDN78P884>`_.
Take a look at a floor architecture plan and guess what the building is intended for:

.. image:: {static}/images/2021_06_11_hexagonal_architecture_in_python_part_1/library_floor_paln.jpg
   :align: center
   :alt: Typical Django project

.. raw:: html

   <details>
   <summary><a>Answer</a></summary>


That is a floor plan of `Oodi Library <https://en.wikipedia.org/wiki/Helsinki_Central_Library_Oodi>`_ in Helsinki.

.. raw:: html

   </details>

I hope this tiny puzzle was easy to solve and you got the main idea:
architecture should meet us at the gate, literally after ``git clone``.
Isn't it great when the source code is organized in such a way
that the purpose and meaning of each file lies on the surface?


Hexagonal architecture of Ports and Adapters
============================================

"We have a Hexagonal architecture of ports and adapters" - how we start
describing the application to new team members.
It follows with demonstration of a weird Cthulhu-like picture:

.. image:: {static}/images/2021_06_11_hexagonal_architecture_in_python_part_1/hexagon.png
   :align: center
   :alt: Hexagonal architecture


Alistair Cockurn the inventor of term "Hexagonal architecture" explains
that "hexagon" is not strictly necessary:

  The hexagon is not a hexagon because the number six is important,
  but  rather to allow the people doing the drawing to have room
  to insert  ports and adapters as they need,
  not being constrained by a  one-dimensional layered drawing.

  The term ‘’hexagonal architecture’’  comes from this visual effect.

  -- `Alistair Cockburn <https://alistair.cockburn.us/hexagonal-architecture/>`_



**Domain** is the heart of an application.
The names of classes, methods, functions, constants and other objects
resemble those of the problem domain.
Think of StackOverflow:

  To vote, one must have 15 or more reputation points.

That is a pure domain rule.
And Guess what?
HTTP, SQL, RabbitMQ, AWS and so on do not belong here.

That technological feast happens in **adapters** which can are connected to the **ports**.
Commands and queries are entering the application through **driver** or API ports.
Commands and queries from the application are directed through **driven** ports.
They are also called Service Interface Provider or SPI ports.


**Application services** are the conductors which control domain and ports
performing an application use case scenario.
As a side note - it is an application service which controls
whether scenario internals are executed in a single transaction.

All this - ports, adapters, application and domain services,
as well as domain objects - are application **layers**.
Each layer consists of individual **components**.
And the grand commandment of the layers interaction is
"*Dependencies are directed from outer layers to the inner side.*"
For example, adapters can use domain objects, but domain should not refer to adapters.


And... THAT IS IT!
The basic principles of Hexagonal architecture of ports and adapters
are surprisingly simple.
This kind of architecture works well in application with complex problem domain.
But it is an overkill for solutions where good old Active Record something
like a "HTTP interface for a database".

We are now ready to dive into building a Hexagonal architecture -based
Django application.
Stay tuned for part II.
