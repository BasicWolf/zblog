Linux, it's time to wake up!
============================

:slug: linux_time_to_wake_up
:categories: Articles
:tags: Linux, ACPI
:date: 2010-05-22 12:00

:summary: Back in my "Windows" times, I was a fan of Foobar2000 music player. One of my favourite plug-ins was "Alarm", which could turn user's computer on during "suspend" state. So, I could switch my laptop to "sleep" mode, and be awaken in the morning by music from Foobar's playlist :) Is it possible to reproduce a similar trick in Linux? It depends on your hardware. Let's give it a try!


What is RTC and ACPI?
---------------------
A Real Time Clock (RTC) alarm is a feature that can be used to allow a
computer to 'wake up' after shut down to execute tasks every day or on a
certain day. It can sometimes be found in the 'Power Management' section
of a motherboard's BIOS setup [1]_.

In computing, the Advanced Configuration and Power Interface (ACPI)
specification provides an open standard for unified operating system-centric
device configuration and power management. ACPI, first released in December
1996, defines platform-independent interfaces for hardware discovery,
configuration, power management and monitoring [2]_.

ACPI allows control of power management from within the operating system.
The previous industry standard for power management, Advanced Power Management
(APM), is controlled at the BIOS level. APM is activated when the system
becomes idle: the longer the system idles, the less power it consumes (e.g.
screen saver vs. sleep vs. suspend). In APM, the operating system has no
knowledge of when the system will change power states [3]_.

ACPI can typically be configured from within the operating system. This is
unlike APM where configuration often involves rebooting and entering the
BIOS configuration screens to set parameters.

The ACPI specification defines seven states (so-called global states) for
an ACPI-compliant computer-system [4]_. Some of them are:

* **G0 (S0)** Working.
* **G1** Sleeping (subdivides into the four states S1 through S4).
* **G1/S3** Commonly referred to as Standby, Sleep, or Suspend to RAM.
  RAM remains powered
* **G1/S4** Hibernation or Suspend to Disk. All content of main memory
  is saved to non-volatile memory such as a hard drive, and is powered down.
* **G2 (S5)** Soft Off. G2, S5, and Soft Off are synonyms. G2 is almost the
  same as G3 Mechanical Off, but some components remain powered so the
  computer can "wake" from input from the keyboard, clock, modem, LAN, or
  USB device.

If implemented, the Real Time Clock alarm must generate a hardware wake
event when in the sleeping state. The RTC can be programmed to generate
an alarm. An enabled RTC alarm can be used to generate a wake event when
the system is in a sleeping state.

Setting up the wakeup alarm
---------------------------
1. Open a terminal and switch to root su root.
2. Check if rtc is available (kernel 2.6.22 and higher):
   ``ls /sys/class/rtc/rtc0/``
3. Look for the wakealarm file.
4. Initialize the alarm via ``echo 0 > /sys/class/rtc/rtc0/wakealarm``.
5. Check if it has been initialzed: ``cat /proc/driver/rtc``. At this
   point, the output should be similar to:

.. code-block:: shell

  rtc_time	: 09:30:05
  rtc_date	: 2010-05-22
  alrm_time	: 09:34:43
  alrm_date	: ****-**-22
  alarm_IRQ	: no
  alrm_pending	: no
  24hr		: yes
  periodic_IRQ	: no
  update_IRQ	: no
  HPET_emulated	: yes
  DST_enable	: no
  periodic_freq	: 1024
  batt_status	: okay

The rtc alarm is now ready to be set up. Wakealarm accepts the number of
seconds since Jan 1, 1970 (this is known as "unix time", "POSIX time" or
"epoch time").

You must make sure that your BIOS clock is set to UTC time - not localtime
- otherwise it will wakeup at the wrong time. However, it is still possible
if the BIOS clock is set to localtime (likely if you also run windows); see
the section below for how to set the alarm correctly when the BIOS clock is
in localtime. If you want to change the wakealarm time, you will need to
write the new wakealarm time to the BIOS.

6. A simple way to set the alarm to current time + 1 minute is:
   ``echo "+60" > /sys/class/rtc/rtc0/wakealarm``.
7. Check if the alarm has been set up:
   ``cat /proc/driver/rtc``


.. code-block:: shell

  ...
  alarm_IRQ      : yes
  ...

8. Now, suspend or shut down your computer. And wait until it wakes up in
   less than a minute :)

You can find more information about the topic at
`MythTV.org <http://www.mythtv.org/wiki/ACPI_Wakeup>`_.

Be careful with the experiments!

References
----------

.. [1] `Wikipedia.org: Real-time alarm
       <http://en.wikipedia.org/wiki/Real-time_clock_alarm>`_
.. [2] `Wikipedia.org: ACPI
       <http://en.wikipedia.org/wiki/Advanced_Configuration_and_Power_Interface>`_
.. [3] `Wikipedia.org: ACPI power states
       <http://en.wikipedia.org/wiki/Advanced_Configuration_and_Power_Interface#Power_States>`_
.. [4] `About ACPI by Emma Jane Hogbin
       <http://www.tldp.org/HOWTO/ACPI-HOWTO/aboutacpi.html>`_
