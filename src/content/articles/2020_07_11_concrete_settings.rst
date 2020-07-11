Concrete Settings: a new way to manage configurations in Python projects
========================================================================

:slug: concrete_settings
:categories: Articles
:tags: programming, library, python, concrete settings
:date: 2020-07-11 13:06

After two years of developing a hobby project,
I am proud to announce **Concrete Settings** -
a new configuration management library for Python projects.

Concrete Settings was born as an effort to improve configuration handling in
a huge decade-old Django application with exceedingly bloated ``settings.py``.
Remember that ``settings.py`` starts with Django configuration only?
What could go wrong if you start adding *application* settings to the file?
One setting, two settings, four...

.. code-block:: python

   FEATURE_X = 123
   FEATURE_Y_ENABLED = True
   FEATURE_Z = 'square'

In time there were so many settings, that developers loose track of them.
The documentation was scattered around issues tracking tool and outdated wiki pages.
There was little or no settings validation - sometimes customers were getting
``HTTP 500 - Internal Server Error`` due to typo in a setting value.

Concrete Settings does its best to tackle these problems.


Why?
----

I was thinking a lot of a developer's and end-user's experience.
How would Concrete Settings library differ from the existing solutions?

After months of experimenting and juggling ideas, the following
ideas laid the foundation:

* Settings with their validation rules and documentation are defined in classes.
* Validation can happen independently from the application, allowing early fails.
* Settings definitions can be nested and mixed.
* Application can read settings from developer-defined sources, like
  yaml / json / python files, environmental variables etc.
* All these are based on Python metaclassing and other capabilities
  to minimize the amount of code written by an end-developer.

From an end-user's perspective:

* Settings are defined in sources. User works with ``application.yml`` or ``configuration.json``
  environmental variables or custom solutions instead of overbloated ``settings.py``.
* An immediate and verbose feedback is received if settings values are invalid.


Enough words, show me the code!
-------------------------------

Let's take a look at a simple example and see the bells and whistles
(aka cool features) that are in the box.

.. code-block:: python

   # app_settings.py

   from concrete_settings import Settings
   from concrete_settings.contrib.sources import EnvVarSource


   class AppSettings(Settings):

       #: Whether debug mode is enabled
       DEBUG: bool = False

       #: HTTP server host
       HOST: str = '127.0.0.1'

       #: HTTP server listening port
       PORT: int = 8080

   # Verify settings definition and construct settings object
   app_settings = AppSettings()

   # Read settings from sources
   app_settings.update('settings.yml')
   app_settings.update(EnvVarSource())

   app_settings.is_valid(raise_exception=True)

   print(f"Server HOST is {app_settings.HOST} ({AppSettings.HOST.__doc__})")
   print(f"Server PORT is {app_settings.PORT} ({AppSettings.PORT.__doc__})")
   print(f"DEBUG is {app_settings.DEBUG} ({AppSettings.DEBUG.__doc__})")

An end-user is happy with the default ``HOST`` value, but wants to override
the rest of the configuration in ``settings.yml``

.. code-block:: yaml

   PORT: 8081

and set ``DEBUG=true`` via an environmental variable.

The output in this case would be:

.. code-block:: pycon

   Server HOST is 127.0.0.1 (HTTP server host)       # default value
   Server PORT is 8080 (HTTP server listening port)  # settings.yml
   DEBUG is True (Whether debug mode is enabled)     # environmental variable


Document via sphinx-style docstrings
------------------------------------

Concrete Settings allows documenting settings via
``#:`` Sphinx-style comments:

.. code-block:: python

   #: HTTP server host
   #: Format: IPv4 address encoded in a string
   HOST: str = '127.0.0.1'


Documentation can be also passed in an explicit Setting definition.

Let's compare these explicit and implicit definitions:

.. code-block:: python

   class AppSettings(Settings):

       #: HTTP server port
       PORT: int = 8080

       HOST = Setting(
           '127.0.0.1',
           type_hint=str,
           doc='HTTP server host'
       )

Explicit or implicit - the extracted docstring, is stored
to ``Setting.__doc__``:

.. code-block:: python

   print(AppSettings.PORT.__doc__)
   print(AppSettings.HOST.__doc__)


However, wouldn't you agree that ``PORT`` documentation is
way more pleasant to read and maintain?


Validate settings early and...
------------------------------

What if a user makes a typo and the supplied port is not an integer?

Let's change a value in ``settings.yml`` from the first example:

.. code-block:: yaml

   PORT: 8081

to

.. code-block:: yaml

   PORT: "8081"

Running the first example again would raise an exception:

.. code-block:: pycon

   concrete_settings.exceptions.ValidationError: PORT: Expected value of type `<class 'int'>` got value of type `<class 'str'>`.

The validation error message is generated by the default ``ValueTypeValidator``.


... add custom validators with style!
-------------------------------------


Let's craft a validator which checks that port number is equal or greater than ``8000``:

.. code-block:: python

   from concrete_settings import Settings, ValidationError, validate


   def port_validator(value: int, **ignore):
       if not 8000 <= value <= 65535:
           raise ValidationError('Expected value in range 8000..65535')


   class AppSettings(Settings):

       #: HTTP server listening port
       PORT: int = 8080 @validate(port_validator)  # <--- I know you are scrolling, but have you noticed this?


   app_settings = AppSettings()
   app_settings.update('settings.yml')

   print(app_settings.is_valid())
   print(app_settings.errors)

Here we use a decorator-like syntax of so-called *behaviors*
(actually it's a matrix multiplication operator in this case :).

Let's test it out by changing ``PORT`` value in ``settings.yml`` to 80:

.. code-block:: yaml


   PORT: 80

The result of running the snippet above is

.. code-block:: pycon

   False
   {'PORT': ['Expected value in range 8000..65535']}

If you are still uncomfortable with @behaviors - there is an explicit way to
add validators to settings. Simply pass ``validators`` to ``Setting`` constructor:


.. code-block:: python

   class AppSettings(Settings):

       #: HTTP server listening port
       PORT: int = Setting(8080, validators=(port_validator,))


Helpful hierarchies
-------------------

I never liked settings names like ``DB_HOST_ADDRESS``.
Why have flat settings names, with feature, sub-feature,
configuration, sub-configuration... in them?

Concrete Settings prefers composition over flat-style settings declaration,
though it provides both extension and grouping
mechanism for settings. For example, let's define database and logging
settings in separate classes:

.. code-block:: python

   from concrete_settings import Settings

   class DBSettings(Settings):
       USER = 'alex'
       PASSWORD  = 'secret'
       SERVER = 'localhost@5432'

   class LoggingSettings(Settings):
       LEVEL = 'INFO'
       FORMAT = '%(asctime)s %(levelname)-8s %(name)-15s %(message)s'

   class AppSettings(Settings):
       DB = DBSettings()
       LOG = LoggingSettings()

   app_settings = AppSettings()
   print(app_settings.LOG.LEVEL)

At first glance, there is nothing special about this code.
What makes it special and somewhat confusing is
that class ``Settings`` is a subclass of ``Setting``!
Hence, nested Settings behave and can be treated
as Setting descriptors - have validators, documentation
or bound behavior.

Additionally, validating top-level settings
automatically cascades to all nested settings.
The following example ends up with a validation error:

.. code-block:: python

   from concrete_settings import Settings

   class DBSettings(Settings):
       USER: str = 123
       ...

   class AppSettings(Settings):
       DB = DBSettings()
       ...

   app_settings = AppSettings()
   app_settings.is_valid(raise_exception=True)

.. code-block:: pytb

   Traceback (most recent call last):
       ...
   concrete_settings.exceptions.ValidationError: DB: Expected value of type `<class 'str'>` got value of type `<class 'int'>`

Finally, the settings can be read from a similarly nested structure. For example ``settings.json``:

.. code-block:: json

   "DB": {
       "USER": "admin"
   }

or environmental variable ``DB_USER``.


In a retrospective
------------------

This project took a long time to develop. What I did right was
no releasing an unfinished and buggy library. That is probably also
what I did wrong. Trying to polish everything before the first
public release without getting any users feedback is not the best
way to go. Hopefully, there will be feedback and the project
would steer towards its users needs and wishes.

Let's start!
------------

Install it via pip:

.. code-block:: shell

   pip install concrete-settings

and check out the
`documentation <https://concrete-settings.readthedocs.org>`_!
