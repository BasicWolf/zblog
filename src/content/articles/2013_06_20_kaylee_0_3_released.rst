.. _kaylee_0_3:

Kaylee v0.3
===========

:slug: kaylee_0_3_released
:categories: Articles
:tags: Kaylee, Python, programming
:date: 2013-06-20 12:00

:summary: Ladies and Gentlemen! I am proud to announce that Kaylee v0.3 has been finally released!

What is new in Kaylee 0.3
-------------------------

* `Kaylee environment and project management scripts`_
* `Built-in debug server`_
* `Native Werkzeug framework support`_
* `Demo projects repository`_
* `Updated unit tests and massive code improvements`_

.. _Kaylee environment and project management scripts:

Kaylee environment and project management scripts
.................................................

This is the sweetest feature of Kaylee. Since the first release I felt
that although Kaylee may be an interesting project to an end user
(meaning a programmer), it has a pretty big fence which one has to jump
over to start using it. The tutorial was written in a plain and simple
language, yet a user had to create a `Makefile`, learn about Kaylee's
recursive-make-based build system and perform some other simple but
inconvenient operations.

The best way out of this were management scripts inspired by the *Django*
framework. Now, a user can simply run:


.. code-block:: none

   python kaylee-admin.py startenv myenv

to create a Kaylee development environment directory with a management
script inside it. The management script helps creating, building and testing
the projects, e.g.:

.. code-block:: none

   python klmanage.py startproject FastPI

\- creates a ``fastpi`` directory  with the project's server and client-side
skeletons.


.. _Built-in debug server:

Built-in debug server
.....................

This feature is about testing and debugging your project without installing
a 3d party web server. Simply execute

.. code-block:: none

   python klmanage.py run

after building the environment. The command starts a local web server, and
launches the first available application defined in the environment's
``settings.py``. The application is then by-default accessible via
http://127.0.0.1:5000


.. _Native Werkzeug framework support:

Native Werkzeug framework support
.................................

Now you can easily integrate Kaylee into your Werkzeug_ -based web application
via native API. This is the third front-end framework which is supported by
Kaylee out-of-the box. The other two are Django_ and Flask_.


.. _Demo projects repository:

Demo projects repository
........................

At last, all Kaylee demo projects, including the tutorial project are
gathered under a separate repository on github:
https://github.com/BasicWolf/kaylee-demo-projects
In addition to the projects, the repository includes a special build script
which automatically creates a Kaylee demo environment, builds the projects
and starts the built-in debug server.


.. _Updated unit tests and massive code improvements:

Updated unit tests and massive code improvements
................................................

Finally, there are lots of code improvements covered with unit tests.
All to make sure that Kaylee would be solid-stable the day it reaches
the maturity version :)


Are you ready to rock?
----------------------

Find more information about Kaylee at http://kaylee.znasibov.info.

.. _Werkzeug: http://werkzeug.pocoo.org
.. _Django: http://djangoproject.com
.. _Flask: http://flask.pocoo.org
