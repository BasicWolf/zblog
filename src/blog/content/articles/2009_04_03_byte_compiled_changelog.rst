Byte-compiled ChangeLog
=======================

:slug: byte_compiled_changelog
:date: 2009-04-03 12:00
:tags: programming, Emacs, Elisp, regex
:category: Articles

:summary: My favourite all-purpose, extensible and customizable editor is Emacs. Mastering Emacs takes months, even years, and there is always a lot to discover. For example, I've just seen how Emacs tried to byte-compile a simple ChangeLog text document. How could that happen?

My dot emacs file is divided into .el pieces like this:

.. code-block:: elisp

  (load "~/.emacs/conf/env_internal.el")
  (load "~/.emacs/conf/env_external.el")
  (load "~/.emacs/conf/ui.el")
  ; ...

It's much easier to deal with functions grouped in different files rather
than functions in one big ``.emacs.el``.

The following "trick" automatically byte-compiles .el files as they're
being saved in Emacs:

.. code-block:: elisp

   (defun autocompile nil
     (interactive)
     (require 'bytecomp)
     (if (numberp (string-match ".el" buffer-file-name))
	   (byte-compile-file (buffer-file-name))))

   (add-hook 'after-save-hook 'autocompile)


It worked perfect for me, until once I was updating a single ChangeLog file
via Emacs. When I saved it, Emacs tried to byte-compile the file! That was
weird.

The error should have not been in Emacs (that's true for 99.9%
Emacs-related "bugs"), but somewhere in one of my configuration .el files.
And probably there was something wrong with the byte-compile-on-save hook.
The only function that could cause it was:

.. code-block:: elisp

  (if (numberp (string-match ".el" buffer-file-name))

Let's see what Emacs says about the ``string-match()`` function:

.. epigraph::

  ``(string-match regexp string & optional start)``

  Returns the index of start of the first match for regexp in string,
  or ``nil``.


So, ``string-match()`` works with regexps! And I have the "." symbol in
the pattern. But period stands for a special character in regexps:

.. epigraph::

  ``'.' (Period)``
  is a special character that matches any single character except a
  newline. Using concatenation, we can make regular expressions
  like ``'a.b'``, which matches any three-character string that begins
  with ``'a'`` and ends with ``'b'``.

  -- Emacs help


So, ``(string-match ".el" buffer-file-name)`` function call is wrong! For
example:

.. code-block:: elisp

  (string-match ".el" "ChangeLog")

returns 4.

I had to use a backslash to quote that period, like this:

.. code-block:: elisp

  (string-match "\.el" "ChangeLog")

But somehow, that didn't work either. An additional documentation exploration
had shown that

.. epigraph::

  When you use regular expressions in a Lisp program, each ``'\'`` must be
  doubled.

  -- Emacs help

Finally, I tried:

.. code-block:: elisp

  (string-match "\\.el" "ChangeLog")

And it worked! The result was `nil`. And the result for any file with .el
extension was the start position of the ".el" string in file's name.


Here is the final version for automatic byte-compile when saving a file with
.el extension:

.. code-block:: elisp

   (defun autocompile nil
     "compile itself if contains .el"
     (interactive)
     (require 'bytecomp)
     (if (numberp (string-match "\\.el" buffer-file-name))
         (byte-compile-file (buffer-file-name))))

   (add-hook 'after-save-hook 'autocompile)


That was a funny problem and it took me about half an hour to deal with.
Emacs help helps :)
