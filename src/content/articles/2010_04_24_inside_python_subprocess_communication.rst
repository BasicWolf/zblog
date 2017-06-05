Inside Python subprocess communication
======================================

:slug: inside_python_subprocess_communication
:categories: Articles
:tags: programming, Python
:date: 2010-04-24 12:00

:summary: Sometimes, it's really hard to understand what happens inside a function or even a whole module of Python's Standard library. For example, the subprocess module contains a very tricky Popep class. I tried to use the the module to communicate with a MATLAB subprocess shell (e.g. send MATLAB commands to subprocess and read the output). Unfortunately I failed and was just able to pass a MATLAB script via command-line arguments. Yet, I learnt much about the ``Popen.communicate()`` method and I'd like to share this knowledge with you.

Before we begin
---------------
I love Python and try using the latest versions when possible. But this
article is about the subprocess module in Python 2.6. Is there a good
reason for that? For starters, you can find this comment in Python 3.1's
subprocess module:

.. code-block:: python

  # XXX Rewrite these to use non-blocking I/O on the
  # file objects; they are no longer using C stdio!

Then, there is a pending `Asynchronous I/O For subprocess. Popen PEP-3145.
<http://www.python.org/dev/peps/pep-3145>`_ Last, but not least, a

.. epigraph::

   *temporary moratorium (suspension) of all changes to the Python language
   syntax, semantics, and built-ins for a period of at least two years from
   the release of Python 3.1*

was proposed and accepted in PEP 3003. Yet,

.. epigraph::

   *..As the standard library is not directly tied to the language definition
   it is not covered by this moratorium.*


A simple experiment
-------------------

.. code-block:: python


  import subprocess

  proc = subprocess.Popen(['ls', '-l'],
                          cwd='/',
                          stdout=subprocess.PIPE)
  out, err = proc.communicate()
  print(out)


This one is really easy: the ``ls`` command with the ``-l`` switch is
executed, the root is set as a current working directory and a pipe is
created to get the data written by ls to ``stdout``.

Why use communicate? Why not write the data directly to ``Popen.stdin``
and read from ``Popen.stdout``?

The official documentation says:

.. epigraph::

   Use ``communicate()`` rather than
   ``Popen.stdin.write``, ``Popen.stdout.read`` or ``Popen.stderr.read``
   to avoid deadlocks due to any of the other OS pipe buffers filling up
   and blocking the child process.


Let's try ``communicate()`` with a long-term shell process:

.. code-block:: python

  import subprocess

  proc = subprocess.Popen('bash',
                          cwd='/',
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

  out, err = proc.communicate('ls')
  print(out)

  out, err = proc.communicate('ls -l')


With successful first communicate() call, you'll receive
``ValueError: I/O operation on closed file`` trying communicate the second
time.

Would you like to know, why an error is raised? It's time to dive deeper
into the code.


Inside Popen.communicate()
--------------------------
You can find the original and complete code of subprocess module in e.g.
``/usr/lib/python2.6/subprocess.py``.

**Note the comments!**

.. code-block:: python

  def communicate(self, input=None):
     """Interact with process: Send data to stdin.  Read data from
     stdout and stderr, until end-of-file is reached.  Wait for
     process to terminate.  The optional input argument should be a
     string to be sent to the child process, or None, if no data
     should be sent to the child.

     communicate() returns a tuple (stdout, stderr)."""

     # Optimization: If we are only using one pipe, or no pipe at
     # all, using select() or threads is unnecessary.
     if [self.stdin, self.stdout, self.stderr].count(None) >= 2:
        stdout = None
        stderr = None
        if self.stdin:
           if input:
              self.stdin.write(input)
           self.stdin.close()
        elif self.stdout:
           # This happens in the experiment we ran above
           stdout = self.stdout.read()

           # Note, stdout is closed!
           self.stdout.close()
        elif self.stderr:
           stderr = self.stderr.read()
           self.stderr.close()

        # Waiting until process terminates!
        self.wait()

        return (stdout, stderr)

     # The most interesting case, two or more pipes opened
     # Remember, self is an instance of subprocess.Popen class
     return self._communicate(input)


Python was made to be cross-platform. On the other hand Python is generally
used on POSIX-compatible operating systems. Let's skip the ``if mswindows:``
part and get to the POSIX methods block:

.. code-block:: python

  def _communicate(self, input):
      # there is a historical reason calling this variables "sets"
      # see select.select() (below)
      read_set = []
      write_set = []

      # returned variables
      stdout = None
      stderr = None

      # the tricky part starts right here
      if self.stdin:
          # Flush stdio buffer.  This might block (!), if the user has
          # been writing to .stdin in an uncontrolled fashion.
          self.stdin.flush()

          # Data to be sent to the process through the pipe
          if input:
              write_set.append(self.stdin)
          else:
              self.stdin.close()

      if self.stdout:
          read_set.append(self.stdout)
          stdout = []
      if self.stderr:
          read_set.append(self.stderr)
          stderr = []

      input_offset = 0

      # ...


This part was not hard at all.
It'll be a little bit harder in the next block: please read the
``select.select()``[1]_ documentation if you're not familiar with the
``select()`` system call.

.. code-block:: python

   #...
   # while read_set contains self.stdout
   # or write_set contains self.stdin
   while read_set or write_set:
       try:
          # man select
          # .. select() allows a program to monitor multiple file descriptors,
          # waiting until one or more of the file descriptors become "ready"
          # for some class of I/O operation (e.g., input possible).
          # A file descriptor is  considered ready if it is possible to perform
          # the corresponding I/O operation (e.g., read) without blocking
          rlist, wlist, xlist = select.select(read_set, write_set, [])
       except select.error, e:

          # EINTR means "This call did not succeed because it was interrupted.
          # However, if you try again, it will probably work."
          # In other words, EINTR is not a fatal error, it just means
          # you should retry whatever you were attempting.
          if e.args[0] == errno.EINTR:
              continue
          raise

       if self.stdin in wlist:
          # When select has indicated that the file is writable,
          # we can write up to PIPE_BUF bytes without risk
          # blocking.  POSIX defines PIPE_BUF >= 512
          chunk = input[input_offset : input_offset + 512]
          bytes_written = os.write(self.stdin.fileno(), chunk)
          input_offset += bytes_written
          if input_offset >= len(input):
             # stdin is closed! It's not possible communicate(input) any more.
             self.stdin.close()
             write_set.remove(self.stdin) # write_set is empty now

       if self.stdout in rlist:
           data = os.read(self.stdout.fileno(), 1024)
           if data == "":
               self.stdout.close()
               read_set.remove(self.stdout)
           stdout.append(data)

       if self.stderr in rlist:
           data = os.read(self.stderr.fileno(), 1024)
           if data == "":
              self.stderr.close()
              read_set.remove(self.stderr)
           stderr.append(data)

       #...


Note, that ``os.write()`` and ``os.read()`` functions are being used.
This functions are intended for low-level I/O. If the end of the file
referred to by file descriptor (e.g. ``self.stdout.fileno()``) has been
reached, an empty string is returned (the ``if data == "":`` conditions).


.. code-block:: python

   #...
   # The while read_set or write_set: loop ends here
   # All data exchanged.  Translate lists into strings.
   if stdout is not None:
       stdout = ''.join(stdout) # (stdout) is a list
   if stderr is not None:
       stderr = ''.join(stderr)

   # Translate newlines, if requested.  We cannot let the file
   # object do the translation: It is based on stdio, which is
   # impossible to combine with select (unless forcing no
   # buffering).
   if self.universal_newlines and hasattr(file, 'newlines'):
       if stdout:
          stdout = self._translate_newlines(stdout)
       if stderr:
          stderr = self._translate_newlines(stderr)

   self.wait() # wait until process terminates
   return (stdout, stderr)

If Python was built with the ``--with-universal-newlines`` option in
configure (the default), the ``file.newlines`` read-only attribute exists,
and for files opened in universal newline read mode it keeps track of the
types of newlines encountered while reading the file. The
``_translate_newlines()`` method just replaces the Windows-style
(``\r\n``) and Mac-style (``\r``) newlines with ``\n``.

The last pieces of the puzzle:


.. code-block:: python

  def wait(self):
      """Wait for child process to terminate.  Returns returncode
      attribute."""
      if self.returncode is None:
          # Try calling a function os.waitpid(self.pid, 0)
          # Ignore Interrupted System Call (errno.EINTR) errors
          pid, sts = _eintr_retry_call(os.waitpid, self.pid, 0)
          self._handle_exitstatus(sts)
      return self.returncode


References
----------

.. [1] http://docs.python.org/library/select.html#select.select
