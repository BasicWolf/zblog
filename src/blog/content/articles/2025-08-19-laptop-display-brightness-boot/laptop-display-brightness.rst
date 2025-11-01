Fixing low display brightness on LUKS password prompt
#####################################################

:slug: laptop-boot-time-display-brightness
:category: Articles
:tags: archlinux, linux, framework-laptop, laptop, brightness, display
:date: 2025-08-19 22:34
:status: published
:summary:
   The problem:
   The laptop display brightness fluctuates after booting when running on *battery* power.

   .. image:: {static}img/luks-password-prompt.webp
      :align: center
      :alt: Explain what's in the image
      :target: {filename}laptop-display-brightness.rst

.. image:: {static}img/luks-password-prompt.webp
   :align: center
   :alt: LUKS password prompt

**Given:**

* Framework Laptop 13 AMD 7040 edition;
* Arch Linux with busybox-based initrd;
* Encrypted drive: LVM partitions on LUKS

**The problem:** The laptop display brightness fluctuates after booting when running on *battery* power.

1. At first, the brightness is rather high, and systemd-boot entries
   are clearly visible.
2. However, after selecting the kernel to boot, the brightness drops to minimum.
   You hardly see anything when the boot reaches LUKS password prompt.
3. The boot process continues after successfully entering the password.
   When systemd kicks in, the systemd-backlight service restores
   the brightness.

**The solution:** set a brightness on startup via a udev rule.

1. Add a new udev rule which sets brightness through ACPI:

   .. code-block:: udev

      SUBSYSTEM=="backlight", ACTION=="add", KERNEL=="amdgpu_bl1", ATTR{brightness}="20000"

   save it to ``/etc/udev/rules.d/10-backlight.rules``.

2. Include the rule path to mkinitcpio's configuration in ``/etc/mkinitcpio.conf``:

   .. code-block:: udev

      FILES = ("/etc/udev/rules.d/10-backlight.rules")

3. Generate a new initrd by running ``mkinitcpio -P``.
4. Take out the power cable and reboot the machine.
   Enjoy the visible decryption password prompt :).
