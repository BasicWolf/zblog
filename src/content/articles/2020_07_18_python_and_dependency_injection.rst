Python and dependency injection
===============================

:slug: python_and_dependency_injection
:categories: Articles
:tags: programming, python, dependency injection
:date: 2020-07-18 12:00
:status: draft

Dependencies and abstractions
-----------------------------

Beep... beep.. beep... - an alarm clock wakes me up.
I have to get up early and make breakfast for kids.
I depend on alarm being triggered at the right time.
The alarm clock application runs on a mobile phone.
It has a galaxy of dependencies! Software, hardware...
down to the power source and *electricity*. The battery has
to be charged, otherwise the phone won't work at all.
But the electricity for charging has to come from somewhere.
I depend on my energy company to produce and deliver
electricity. And the energy company gets it from
a sources like a solar or a nuclear power plant.
Going deeper and deeper in eventually
brings us to being dependent on the constant
laws of physics!

Dependencies are everywhere. However, is it a concrete
dependency or just its abstract capabilities that we depend upon?

Imagine that you have to make a phone call over GSM phone network.
Does it matter, whether you use an IPhone, or some Android
device, or even a good-old stationary phone?

You are probably reading this article from
a screen - be it a monitor, a mobile device,
or a e-Ink display. It doesn't really matter which one.

Sitting in a car of a train,
we don't care what kind of locomotive - an
electric, diesel or even a steam -powered
pulls the train. Hah, it could be the Superman working out.
I'd be a happy passenger as long as the
locomotive dependency does the job.

Tadaaam! We've just rediscovered the **Dependency Inversion Principle**.
Robert Martin defined the Dependency Inversion Principle in two statements [2]_:

  1. High-level modules should not depend on low-level modules. Both should depend on abstractions.
  2. Abstractions should not depend on details. Details should depend upon abstractions.

Back to the train example, a train (**high-level module**)
does not depend on a kind of the locomotive (**low-level module**).
It simply depends on being pulled (**abstraction**).


Dependencies through eye of the Python
--------------------------------------

Getting back to programming and Python - what is a dependency?
*A dependency is an object, that another object requires.* [1]_.

Let's have at an example function which sends an alert
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
In other words, **message_bus is a dependency of  send_alert()**.


Passing dependencies
....................

Using a global variable as a dependency is simple and easy to start with,
but it quickly becomes a maintenance nightmare.
Consider the kind of "dark magic" required to write a unit test
for ``send_alert`` - the module has to be monkey patched in order
to replace ``message_bus`` with a test double.

Another way would be passing the dependency as a function
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

Testing ``send_alert()`` is now also simple, since
a test double, such as a mocked ``MessageBus`` instance
is explicitly passed to the function.

The huge downside is that ``message_bus`` has to be
passed to every ``send_alert()`` call.

There are different ways to overcome this.



----

For example, ``message_bus`` is imported from
a global application context.

Passing a dependency
to a

This small example comes with a big architectural decision:
``message_bus`` is  passed to ``send_alert()`` via a global
variable.

and is being **injected** into ``send_alert()``
  as a global variable.


What dependency injection is and is not
---------------------------------------


Improved application structure
------------------------------


Targeted unit testing
---------------------


Clean architecture and more
---------------------------

References
----------

.. [1] `Dependency injection in ASP.NET Core <https://docs.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-3.1>`_
.. [2] Robert Martin C. (2003), *Agile Software Development, Principles, Patterns, and Practices*. ISBN 978-0135974445.
