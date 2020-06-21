Concrete Settings: a new way to manage configurations in Python projects
========================================================================

:slug: concrete_settings
:categories: Articles
:tags: programming, library, python, concrete settings
:date: 2020-05-03 12:00
:status: draft


**Concrete Settings** is a new configuration management library for Python projects.

Concrete Settings was born as an effort to improve configuration handling in
a huge decade-old Django application. At the heart of the application
is a ``settings.py`` file, which initially contained Django-specific settings.
What could go wrong if you start adding *application-specific* settings to the file?
One setting, two settings, four...

.. code-block:: python

   FEATURE_X = 123
   FEATURE_Y_ENABLED = True
   FEATURE_Z = 'square'

In time, there were so many settings, that developers loose track of them.
The documentation was scattered around issues tracking tool and outdated wiki pages.
There was little or no settings validation - sometimes customers were getting
``HTTP 500 - Internal Server Error`` due to typo in a setting value.

**Concrete Settings** tries to tackle these problems.
It was built with developers and end-users experience in mind.

Settings with their validation rules and documentation are defined in classes.
Validation can happen independently from the application, allowing early fails.
Concrete Settings prefers composition over flat-style settings declaration,
so settings can be nested and mixed.

An application should not interact with settings definition directly.
Instead, a developer can enable reading application configuration from various sources
like YAML, JSON or Python files, environmental variables and so on.

Let's take a look at a simple example and explore all the bells and whistles
(aka cool features) you can find in Concrete Settings.

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

Concrete Settings uses Sphinx to extract documentation
written in ``#:`` comments above settings definitions
and stores it to ``Setting.__doc__``.
Documentation can be also passed in an explicit Setting
definition.

Let's compare these explicit and implicit definitions:

.. code-block:: python

   class AppSettingsExplicit(Settings):

       HOST = Setting(
           '127.0.0.1',
           type_hint=str,
           doc='HTTP server host'
       )

   class AppSettingsImplicit(Settings):

       #: HTTP server host
       HOST: str = '127.0.0.1'


They are equivalent for Concrete Settings and you can use either.
However, which one is more readable in your opinion?


Validate settings early and...
------------------------------

What if a user makes a typo and the supplied port is not an integer?

Let's change a value in ``settings.yml``:

.. code-block:: yaml

   PORT: 8081

to

.. code-block:: yaml

   PORT: "8081"

Since we are calling ``settings.is_valid()`` with argument ``raise_exception=True``,
a validation error is raised:

.. code-block:: pycon

   concrete_settings.exceptions.ValidationError: PORT: Expected value of type `<class 'int'>` got value of type `<class 'str'>`.


What you see there is ``ValueTypeValidator`` from ``Settings.default_validators`` in action.

... add custom validators with style!
-------------------------------------


Let's craft add a validator which checks that port number is equal or greater than ``8000``:

.. code-block:: python

   from concrete_settings import Settings, ValidationError, validate


   def port_validator(value: int, **ignore):
       if not 8000 <= value <= 65535:
           raise ValidationError('Expected value in range 8000..65535')


   class AppSettings(Settings):

       #: HTTP server listening port
       PORT: int = 8080 @validate(port_validator)


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


Hierarchy is nice
-----------------
