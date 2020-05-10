Concrete Settings: a new way to manage configurations in Python projects
========================================================================

:slug: concrete_settings
:categories: Articles
:tags: programming, library, python, concrete settings
:date: 2020-05-03 12:00
:status: draft


**Concrete Settings** is a new configuration management library for Python projects.

Concrete Settings was born as an effort to improve a configuration of
a huge decade-old Django application. At the heart of the application
is a ``settings.py`` file, which originally contained Django-specific settings only.
What could go wrong if you start adding *application-specific* settings to the file?
One setting, two settings, four...

.. code-block:: python

   FEATURE_X = 123
   FEATURE_Y_ENABLED = True
   FEATURE_Z = 'square'

In time, there are so many settings, that developers loose track of them.

The settings validation is scattered around the code, unless there is no validation
and settings are used in runtime as-is.
Some settings are documented, but the documentation is not generated automatically
from the source files. How soon does the documentation become outdated?

**Concrete Settings** tries to tackle these problems.
It is built around developer's experience and end-user application interaction in mind.

Settings with their validation rules and documentation are defined in classes.
Validation can happen independently from the application, allowing early fails.
Concrete Settings prefers composition over flat-style settings declaration,
so settings can be nested and mixed.

An application should not interact with settings definition directly.
Instead, a developer can enable reading application configuration from various sources
like YAML, JSON or Python files, environmental variables and so on.

Have a look at a simple example:

.. code-block:: python

   from concrete_settings import Settings
   from concrete_settings.contrib.sources import EnvVarSource


   class AppSettings(Settings):

       #: Whether debug mode is enabled
       DEBUG: bool = False

       #: HTTP server listening port
       PORT: int = 8080


   # Verify settings definition and construct settings object
   app_settings = AppSettings()

   # Read settings from sources
   app_settings.update('settings.yml')
   app_settings.update(EnvVarSource())

   app_settings.is_valid(raise_exception=True)
   print(f"Server PORT is {app_settings.PORT} ({AppSettings.PORT.__doc__})")
   print(f"DEBUG is {app_settings.DEBUG} ({AppSettings.DEBUG.__doc__})")

With ``settings.yml`` controlled by an end-user:

.. code-block:: yaml

   DEBUG: false
   PORT: 8081


And an environmental variable ``DEBUG`` set to ``true``, the output is:

.. code-block:: pycon

   Server PORT is 8081 (HTTP server listening port)
   DEBUG is False (Whether debug mode is enabled)


