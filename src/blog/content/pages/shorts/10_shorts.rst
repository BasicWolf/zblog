Shorts
######

:slug: shorts
:status: hidden

Sometimes I just want to put some thoughts on paper without talking too
much about it :)


Oho! GNU/Linux has just upgraded a plugged device firmware!
===========================================================

*2025.09.16* -
Things have changed... a lot! I got a second-hand
HP G5 USB-C docking station and one question I
had somewhere back in mind was
"Where would I find Windows machine to upgrade its firmware?"

Imagine my surprise when this popped out:

.. image:: {static}img/2025.09.16-linux-firmware-upgrade.webp
   :alt: Screenshot of Gnome Software Updates manager proposing USB-C dock firmware upgrade
   :loading: lazy
   :target: {static}img/2025.09.16-linux-firmware-upgrade.webp

That's how I got to know `Linux Vendor Firmware Service <https://fwupd.org/>`_.
I clicked "Update" and in few minutes the dock was running
the latest official proprietary firmware from HP.
It's truly amazing! And btw, Framework Laptop
BIOS (EFI firmware) updates also come through this channel.
My warmest gratitude to people behind this service.

Update your password in a discontinued automotive service
=========================================================

*2025.08.01* -
Renault R-Link store was discontinued in mid-2024.
But today I got an email:

.. image:: {static}img/2025.08.01-rlink-password-change-email.webp
   :alt: Email asks me to change the password
   :loading: lazy
   :target: {static}img/2025.08.01-rlink-password-change-email.webp

And surprise-surprise, opening the link ends in an SSL error.
This is interesting because the main service was turned off, but
somewhere deep inside the infrastructure an authentication(?)
service is still alive, sending emails about expired passwords.
