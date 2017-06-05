Awesome WM is truly awesome!
============================

:slug: awesome_wm_is_awesome
:categories: Articles
:tags: Awesome, window manager
:date: 2015-12-20 21:00


:summary: I have never though of changing a window manager. In fact I was not aware of different window manager types at all. I've been using stacking window manager since almost forever! And you are very familiar with it, that is the one still encountered in Windows, in has been in MacOS even earlier, it is in GNOME, KDE and XFCE by-default. Are there any alternatives?

A window manager is system software that controls the placement and appearance of windows within a windowing system in a graphical user interface [1]_.
Here is an example from Windows 95 era:

.. image:: {filename}/images/2015_12_20_awesome_win95.jpg
   :alt: Windows 95 user interface [Original: http://media.moddb.com/images/games/1/22/21021/Windows95applications.jpg]
   :align: center

The picture should be very familiar. Windows are placed all around the desktop, some windows are overlapping the others. This approach tries to rather emulate the desktop metaphor.

A tiling window manager is a window manager with an organization of the screen into mutually non-overlapping frames, as opposed to the more popular approach of coordinate-based stacking of overlapping objects (windows) [2]_. For example:

**TODO**: Screenshot here

Ironically, my favourite editor Emacs has a built-in tiling window manager in it. Though I've been using Emacs constantly, I never thought of the feature as of a window manager.

What is the catch? Why one would switch from traditional "desktop" look to tiled positioning? Nowadays we have a plenty of space on the monitors which is sometimes not used at all. For example, Twitter or Facebook timelines leaves plenty of space on left and right. Why waste the space? Isn't it tempting to open two or even more windows side-by side and have all the information visible, or at least quickly accessible when you need it?

A good tiling manager provides convenient navigation and automated windows positioning. You can predict where the next window appears and what its size is going to be. This is even more convenient with multiple monitors - you can assign a browser to always appear on the right monitor and Email or IM client on the left one. The navigation between windows is simple and intuitive and is all done via keyboard (also via mouse!).

I am a happy user of **Awesome** WM. Awesome is a highly configurable, next generation framework window manager for X. It is very fast, extensible and licensed under the GNU GPLv2 license. It is primarly targeted at power users, developers and any people dealing with every day computing tasks and who want to have fine-grained control on theirs graphical environment. There are plenty of features that come right out of the box. Let's explore some of them.


Extensibility
-------------

*Awesome* is configured via scripts in Lua programming language. Seriously, the configuration is a Lua file and you can extend it as much as Lua and Awesome API allow. All keyboard and mouse bindings, events, look & feel are configurable (btw, my awesomerc is available on `GitHub <https://github.com/BasicWolf/awesomerc>`_). I only pity that it is not Python :)


Layouts
-------

Awesome comes with various window placing algorithms, i.e. layouts. For example, here is how **columns** layout looks like with 6 windows open:

**TODO**: Screenshot here

With one stroke you can immediately cycle the layouts and rearrange the windows in **rows** manner:

**TODO** Screenshot here



Ready to try?
-------------

Awesome is available in all major distros and is very easy to start with. There are lots of configurations examples available on Github.


.. [1] `Wikipedia: Window manager [20.15.2015]
       <https://en.wikipedia.org/wiki/Window_manager>`_

.. [2] `Wikipedia: Tiling manager [20.15.2015]
       https://en.wikipedia.org/wiki/Tiling_window_manager`_
