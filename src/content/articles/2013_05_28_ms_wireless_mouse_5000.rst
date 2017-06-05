Microsoft Wireless Mouse 5000: The Good, the Bad and the Ugly.
==============================================================

:slug: ms_wireless_mouse_5000
:categories: Articles
:tags: Microsoft, mouse, Linux, life
:date: 2013-05-28 12:00

:summary: I have finally replaced my old *Defender* mouse with a brand-new, wireless blue laser-powered *Microsoft Wireless Mouse 5000*. Some of the reasons for picking this particular mouse are: symmetric, wireless, laser and GNU/Linux support :). A month of usage has passed and there is enough time to write a review with all tips'n'tricks which can help handling this mouse properly.


Why MS Wireless 5000?
---------------------

There is an odd thing people notice, looking and my working place:
the mouse is on the left side. Usually the following question is:
*"Are you left-handed?" - "I'm not!"*.
Long ago my father pointed out that a right-handed person can have a free
hand for other tasks (like writing with a pen) if the mouse remains in the
left hand. I am now more confident having the mouse on the left side, that
on the right. But guess what is the trick in this situation? Most modern
*ergonomical* mice are created for right-handed persons. For example, this
nice Logitech M705:

.. image:: {filename}/images/ms_wireless_mouse_5000/logitech_M705.png
   :align: center
   :alt: logitech m705

One would find very hard times using it with the left hand.
You are probably asking "why not use symmetrical mouse?". And that is
exactly the kind of mouse I've been using since 2005. This is my old
Defender (the blue one):

.. image:: {filename}/images/ms_wireless_mouse_5000/defender_orig.jpg
   :align: center
   :alt: defender mouse

A funny story about it: Back in 2005 I went to a store looking for a USB
mouse, as the PS/2 mouse was not working with the Linux Mandrake distro
(early 2.6 kernel) on my dorm roommate's PC.

All these years the mouse was working perfectly. But then, I married and
started sharing the computer with my wife. Guess how happy she was about
the mouse on the left side :) Dragging the wired mouse here and there
created a mess with all the adjacent cables. It was clear that a time
to buy a wireless mouse had finally come.

Of course, my choice would have been dramatically influenced by the old
mouse. I was looking for something:

* wireless,
* symmetrical,
* big enough to fit my palm,
* with side buttons
* and laser sensor.

I have considered several models, which dropped out of the list one-by-one
(for example the
`Logitech M525 <http://www.logitech.com/en-us/product/wireless-mouse-m525>`_
was not big enough for my palm). In the end, the only mouse that seemed to
fit all these requirements was:

.. image:: {filename}/images/ms_wireless_mouse_5000/mk_wm5000_large.jpg
   :align: center
   :alt: MS Wireles 5000

The Good
--------

My palm lies firmly on the mouse, the dimensions are 7x12 cm (2.8x4.6) inches.
Two AA batteries add weight which gives the overall feeling of a solid device.
The side panels are made from rubbery material. The BlueTrack laser is perfect,
it literally works on any surface (I was able to use it on my kneecap :).
Finally the wireless signal range is at least 3-4 meters (10-13 feet).

The Bad
-------

I have been extensively using the side buttons on the Defender for convenient
forward and back navigation in browsers. The side buttons on Defender are
big and located directly under the thumb and the little finger.
The side buttons on MS 5000 are small and very hard to click as they are
located above of where thumb and little finger are placed:

.. image:: {filename}/images/ms_wireless_mouse_5000/defender_ms_02.jpg
   :align: center
   :alt: ms 5000 vs. defender

I'd wish that was the only problem with the buttons, but there is something
much worse: **the middle button**.
The middle button has a "horizontal scrolling" feature, which can be used
by pushing the button sideways. In practice, 80% of "middle click" ends
up in horizontal scrolling, because the button is very stiff to click.
I use middle click a lot, especially when browsing (e.g. for opening the
links in background tabs). And it became a real headache to perform that
operation with this mouse. Luckily...

The Ugly
--------

Luckily, I am a Debian GNU/Linux user :) With Debian you can easily override
the keymap of any X11 device. For example, it is possible to map the
horizontal scroll buttons as a middle-click!
To do a quick temporal change to the buttons map, run ``xinput``. This is
the output on my computer:

.. code-block:: none

  zaur@z:~% xinput
  ⎡ Virtual core pointer                    	    id=2	[master pointer  (3)]
  ⎜   ↳ Virtual core XTEST pointer              	id=4	[slave  pointer  (2)]
  ⎜   ↳ HID 044e:3012                           	id=10	[slave  pointer  (2)]
  ⎜   ↳ PS/2 Mouse                              	id=17	[slave  pointer  (2)]
  ⎜   ↳ AlpsPS/2 ALPS GlidePoint                	id=18	[slave  pointer  (2)]
  ⎜   ↳ Microsoft Microsoft® 2.4GHz Transceiver v7.0	id=12	[slave  pointer  (2)]
  ⎜   ↳ Microsoft Microsoft® 2.4GHz Transceiver v7.0	id=13	[slave  pointer  (2)]
  ⎣ Virtual core keyboard                   	id=3	[master keyboard (2)]
      ↳ Virtual core XTEST keyboard             	id=5	[slave  keyboard (3)]
      ↳ Sony Vaio Keys                          	id=6	[slave  keyboard (3)]
      ↳ Power Button                            	id=7	[slave  keyboard (3)]
      ↳ UVC Camera (05ca:183b)                  	id=8	[slave  keyboard (3)]
      ↳ HID 044e:3013                           	id=9	[slave  keyboard (3)]
      ↳ AT Translated Set 2 keyboard            	id=16	[slave  keyboard (3)]
      ↳ Microsoft Microsoft® 2.4GHz Transceiver v7.0	id=11	[slave  keyboard (3)]
      ↳ USB2.0 Camera                           	id=14	[slave  keyboard (3)]
      ↳ Topre Corporation Realforce 105U        	id=15	[slave  keyboard (3)]

For some reason there are two *Microsoft Transceivers* devices.
To find the required one, run ``xinput get-button-map device_id``, where
device_id is either 12 or 13, e.g.:

.. code-block:: none

  zaur@z:~% xinput get-button-map 13
  1 2 3 4 5 6 7 8 9 10 11 12 13

In order to set the desired keymap of the device, run the ``xinput`` command
as follows:

.. code-block:: none

  xinput set-button-map 12 1 2 3 4 5 2 2 8 9 10 11 12 13

Here, ``2`` is the code of the middle button which overrides the codes
of "scroll left" and "scroll right" (6 and 7).

To make the change permanent, create a config file (e.g. ``10-ms5000.conf``)
in ``/etc/X11/xorg.conf.d/`` directory, with the following content:

.. code-block:: none

  Section "InputClass"
          Identifier      "MS 5000"
          MatchProduct    "Microsoft Microsoft® 2.4GHz Transceiver v7.0"
          Option          "ButtonMapping" "1 2 3 4 5 2 2 8 9 10 11 12 13"
  EndSection


The conclusion
--------------

Microsoft Wireless Mouse 5000 is 75% worth its money (35EUR),
especially for users who are looking for a big and symmetric mouse.

It has a minor (small side buttons) and a major (stiff middle click) glitches,
which are not that bad to ignore this mouse.

I hope you enjoyed the review. Feel free to comment and share you mouse
experience!
