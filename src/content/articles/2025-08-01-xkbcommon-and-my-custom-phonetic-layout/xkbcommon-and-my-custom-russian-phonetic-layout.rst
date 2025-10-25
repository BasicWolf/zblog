xkbcommon and my custom Russian phonetic layout
###############################################


:slug: xkbcommon-and-my-custom-russian-phonetic-layout
:category: Articles
:tags: linux, xkb, xkbcommon, wayland, layout, russian, phonetic
:date: 2025-08-01 12:00
:status: published
:summary:
   The Soviet Union officially dissolved in 1991, but Russian language remained
   the region's lingua franca for decades.
   Many children of my generation were simultaneous bilinguals;
   we spoke both Azeri and Russian since childhood.
   I learned to type in Russian,
   but I never ever learned the official Windows Russian
   keyboard layout, because I didn't have a keyboard with Russian alphabet
   printed on it.
   The alternative was a phonetic layout, and I still remember
   a program called "Alt-Win", which allowed to select Azeri Latin,
   or Russian phonetic keyboard layouts in Windows 9x.
   Over the years, I used other tools in Windows XP and Windows 7 to recreate
   this layout. And then I moved to Linux.

   In Linux, the only tool you need to create your own keyboard layout
   is a text editor.
   Would you like to find out how?

   .. image:: {static}img/keymap.webp
      :align: center
      :alt: Explain what's in the image
      :target: {filename}xkbcommon-and-my-custom-russian-phonetic-layout.rst


The Soviet Union officially dissolved in 1991, but Russian language remained
the region's lingua franca for decades.
Many children of my generation were simultaneous bilinguals;
we spoke both Azeri and Russian since childhood.
I learned to type in Russian,
but I never ever learned the official Windows Russian
keyboard layout, because I didn't have a keyboard with Russian alphabet
printed on it.
The alternative was a phonetic layout, and I still remember
a program called "Alt-Win", which allowed to select Azeri Latin,
or Russian phonetic keyboard layouts in Windows 9x.
Over the years, I used other tools in Windows XP and Windows 7 to recreate
this layout. And then I moved to Linux.

In Linux, the only tool you need to create your own keyboard layout
is a text editor.
Since you are already reading this, scroll down to feed your curiosity!

.. image:: {static}img/keymap.webp
   :align: center
   :alt: Explain what's in the image


.. note::

   In this article, I refer to Russian phonetic keyboard layouts as keyboard
   layouts where Russian letters are mostly located at their similarly sounding
   letters in English, on US QWERTY keyboard.
   For example, the Russian letters "а", "о", "м", "т" are typed using
   the English "a", "o", "m", "t" keys.

   The trick is to map 33 Russian alphabet letters
   to a keyboard that has only 26 Latin letters (used in English)
   while retaining the necessary punctuation marks.


Custom layout - the naive way
=============================

The naive way to create a custom layout is by modifying an existing
variant definition in one of the symbols files from ``/usr/share/X11/xkb/symbols``.
That's what I originally did — I modified the ``ru`` file and its ``phonetic``
section:

.. code-block:: none

   partial alphanumeric_keys
   xkb_symbols "phonetic" {

       name[Group1]= "Russia - Phonetic";

       key <TLDE>   {[       Cyrillic_yu,       Cyrillic_YU ]};
       key <AE01>   {[                 1,            exclam ]};
       key <AE02>   {[                 2,                at ]};
       key <AE03>   {[                 3,        numbersign ]};
       ...
       ...
   }

Here, the first column contains the symbolic key names [1]_,
the second column contains the corresponding key symbol for a key pressed
without modifiers,
and the last column contains the key symbol for a key pressed with Shift.

This works, BUT your user needs write permissions for the file,
and the file will be overwritten anyway every time XKB gets updated by the system.

Can you believe that for over 15 years I used the same customised ``ru`` symbols
file, and replaced the upstream file over and over?
I did this manually every time the package responsible for ``/usr/share/X11/xkb``
got updated. The file followed me as I moved from Ubuntu to Debian,
and from Debian to Arch. And honestly speaking,
I never bothered to dig deeper and learn the mechanisms behind the command
to set up my desired layouts::

   setxkbmap -layout 'us,fi,ru,az' -variant ',,phonetic,' -option grp:shifts_toggle

That allowed me to cycle through US, Finnish, Russian phonetic and Azeri layouts
by pressing both shifts.

This changed when I installed Arch on
`my new laptop
<{filename}../2025-07-17-framework-laptop-is-awesome/framework-laptop-is-awesome.rst>`_.
I finally decided to find a "smart way" and learn the mechanisms behind
layouts in Linux graphical environments.


Bits about XKB
==============

Imagine a system with a graphical environment backed by Wayland compositor.
Let's find out how pressing a key on the keyboard results in a symbol appearing
in an application. I'll omit deep technicalities to keep the narrative short.

.. figure:: {static}img/xkb-diagram.svg
   :align: center
   :width: 100%
   :alt: Diagram explaining how pressing a keyboard key ends up in application
         while passing through libxkbcommon.
   :target: {static}img/xkb-diagram.svg


   A high-level diagram of how a key press event travels from a keyboard to
   a user-space application.

1. Wayland compositor notifies the application about the current keymap
   configuration. This happens when application starts or the user changes
   keyboard layout.
   The application loads the keymap via **xkbcommon** library.
2. The keyboard device sends a hardware signal - a *scancode*
   to the Linux Kernel.
3. The kernel's evdev subsystem
   maps the scancode to a *keycode* - a representation abstracted from hardware.
4. Wayland compositor uses libinput to receive keyboard and other input
   device events from the kernel. It notifies the application (a Wayland client)
   about a pressed/released key with a *keycode*, and *modifiers*.
5. The application (using GTK, Qt, or other Wayland client implementations)
   passes the *loaded keymap context*, the *keycode* and *modifiers* to **xkbcommon**.
6. xkbcommon applies keycodes/compat/geometry/symbols/types (KcCGST)
   configuration [2]_, to map the input to the final symbol.

In a nutshell, it's xkbcommon's job to translate
``Shift + L`` keystroke to Cyrillic ``Л`` symbol, when I have my Russian
phonetic layout activated.

As Daniel Stone, the maintainer of xkbcommon nicely puts it:

..

  It’s about two things: parsing and loading keymaps, and managing their
  ongoing state. State, in terms of keyboards, is the usual suspects —
  modifiers (e.g. Shift, Alt), multiple layouts (mostly for multiple languages),
  and LEDs. In general, you only want one person keeping a canonical copy
  of the state, and distributing it to its clients, as both the X server
  and Wayland do today.
  xkbcommon allows for this mode of operation, and is indeed how all
  current Wayland clients handle keyboard input [3]_.


Historical reference
--------------------

X Keyboard Extension (XKB) protocol
was developed in early 1990s and included in
X Window System, Version 11 Release 6 (X11R6) in May 1994 [4]_.
XKB extends the core X protocol by offering support for

* Multiple keyboard layouts
* Sophisticated modifier handling
* LED control
* Keyboard geometry description,
* Various keyboard behaviors beyond what the core X protocol provides [5]_.

Rather than reinventing the wheel, Wayland protocol currently relies on XKB
format for keymaps. Unlike X11, where clients received a symbolic representation
of the key, in Wayland it's up to the clients to interpret keyboard
events and map the pressed keys to symbols.
xkbcommon library is typically used for this purpose.


Custom layout - the smart way
=============================

The xkbcommon documentation comes with a tutorial on adding a custom
keyboard layout [6]_.
I don't want to repeat that here, and rather encourage you to dive
into it and get the information from the original source.

However, I'll briefly describe my Russian Alternative Phonetic setup.


1. | **Symbols file:**
   | I placed my custom layout variant in a new symbols file
     ``$HOME/.config/xkb/symbols/ru_alternative``.
     This file contains translation of symbolic key codes into the desired
     key symbols (`link <{static}data/ru_alternative.html>`__).

2. | **Rules file:**
   | I added a rule to ``~/.config/xkb/rules/evdev`` file
     (`link <{static}data/evdev.html>`__).
     The purpose of the rules file is to map between user-friendly configuration,
     and the configuration used by *xkbcomp* keymap compiler [7]_.
3. I made the layout discoverable in GNOME by adding an entry to
   ``~/.config/xkb/rules/evdev.xml`` (`link <{static}data/evdev.xml.html>`__).

That's it! A simple solution for a single-person machine,
and no more half-baked solutions with broken layouts after
system updates :)


References
==========

.. [1] `xkbcommon - The XKB keymap text format, V1 / Keycode <https://xkbcommon.org/doc/current/keymap-text-format-v1.html#keycode-def>`_.
.. [2] `xkbcommon - RMLVO vs. KcCGST <https://xkbcommon.org/doc/current/user-configuration.html#rmlvo-vs-kccgst>`_.
.. [3] `xkbcommon: what is it? <https://www.fooishbar.org/blog/xkbcommon-intro/>`_
.. [4] `X Window System, Version 11 release 6 (X11R6) <https://www.x.org/wiki/X11R6/#index16h4>`_.
.. [5] `DeepWiki - X Keyboard Extensions <https://deepwiki.com/mirror/libX11/5-x-keyboard-extension-(xkb)>`_.
.. [6] `xkbcommon - User Configuration <https://xkbcommon.org/doc/current/user-configuration.html>`_
.. [7] `xkbcommon - Rule file format <https://xkbcommon.org/doc/current/rule-file-format.html>`_
