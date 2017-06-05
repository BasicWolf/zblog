The legacy of the initramfs optimization
========================================

:slug: the_legacy_of_the_initramfs_optimization
:date: 2009-01-11 12:00
:categories: Articles
:tags: initramfs, Linux
:summary: An adventure of dealing with ``Target filesystem doesn't have /sbin/init``


I was shocked receiving the ``Target filesystem doesn't have /sbin/init``
message. I've surfed the Internet for possible solutions - none of them
helped. I had to remember everything I've changed in my system during
past 3 months. Finally, I remembered..

I'm a Linux person. I'm a Linux person since March 2008. My current OS is
Ubuntu Linux (x86). But I don't like to be "generic". My x64 processor is not
generic, it's Core2. I have one particular Ethernet, wi-fi and bluetooth
adapter, one sound and video card. I'll never use the 95% of Linux-supported
hardware..

So, I've compiled my custom "sony-vaio" kernel, still always downloaded the
generic kernel upgrades (to have a native kernel full of modules in a case
of emergency).

This happened when I've updated the system.

Ubuntu has downloaded the linux-image-2.6.11-generic kernel. I wanted to
check, If my motioneye camera works under it, so, I rebooted the computer
and selected the **Ubuntu 8.10, kernel 2.6.27-11-generic** option. Bump!

``Target filesystem doesn't have /sbin/init``

I had no ideas of what did that mean. I rebooted the laptop via
**Ctrl+Alt+PrintScreen+B**. Fortunately my custom kernel was working fine.
After an hour of surfing the Internet I already knew, that possibly the
kernel can't mount a root file system. So, the difference was between my
custom kernel and the generic kernel. I was annoyed. There was nothing in my
kernel, that  generic kernel didn't have. But wait! While creating my custom
kernel, I've compiled the ext3 filesystem support **statically** into it.
But why the generic kernel can't load the ext3 module?

Suddenly it dawned upon me.

There is initial ram disk stuff at the beginning of system load process.

  The initial ramdisk, or initrd is a temporary file system commonly used
  by the Linux kernel during boot. The initrd is typically used for making
  preparations before the real root file system can be mounted [#]_

So, possibly the initrd image created for the generic kernel didn't contain
the ext3 module. How could that happen? It could, if you're a person who
likes to optimize everything that could be optimized. For example, the
system's boot-time.

There is a minimal set of modules enough to load a system both from hibernate
(suspend2disk) and powered-off conditions. By default, the initrd contains
"most" modules (see /etc/initramfs-tools/initramfs.conf file). In my case the
MODULES option was changed like this:


.. code-block:: none

  #MODULES=most
  MODULES=list


I used next steps to generate the modules list:

1. Boot kernel with ``init=/bin/sh`` option
2. Execute ``sudo lsmod | tail -n +2 | sort | awk '{print $1;}' >
   /etc/initramfs-tools/modules``
3. Execute ``update-initramfs -v -d -k
   \`uname -r` && update-initramfs -v -c -k \`uname -r```

The second line copies all loaded modules' names to
``/etc/initramfs-tools/modules`` file. The third line updates the current
kernel's initramfs file.

As you might already found out, there was no ext3 module in the list, because
my custom kernel didn't need an ext3 module!

But Ubuntu's generic kernel has the ext3 as a module!
So, to boot a system with generic kernel, I should have had an "ext3" line
in ``/etc/initramfs-tools/modules``.

It didn't take long. I updated the file and called
``update-initramfs -c -k all``
to regenerate the init ram disks for both kernels (actually I didn't need
to do that for my custom kernel :).

At last, I could load the system with new 2.6.27.11 kernel.


.. [#] http://en.wikipedia.org/wiki/Initrd
