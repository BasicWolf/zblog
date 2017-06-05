Inside Python: understanding os.listdir()
=========================================

:slug: inside_python_understanding_os_listdir
:categories: Articles
:tags: programming, Linux, Python, C
:date: 2011-05-08 12:00

:summary: If you've been using python for a long time, then you surely know that ``os.listdir()`` function returns an unsorted list of file names. I didn't care much until facing a situation, in which the sorted-sequential processing of files was crucial, and I could not remember whether the previous file processing were done in sorted order. Well, luckily they were. But hey, this is a little bit annoying, isn't it? Why ``os.listdir()`` returns an unsorted list of files? Would you like to find out?

To answer this question, one has to get inside Python's source.
The stable Python 3.2 could be found
`here <http://www.python.org/download/releases/3.2>`_.
The ``os.py`` module in source archive's Lib directory doesn't contain the
``listdir()`` function. Yet, the very place to look comes from:

.. code-block:: python

   from posix import *

Let's take a look on ``Modules/posixmodule.c``:

.. note::

   Pay attention to the comments!

.. code-block:: c

   static PyObject *
   posix_listdir(PyObject *self, PyObject *args) /* line 2323 */
   {
       /* POSIX-related code, supposed to start from line 2574 */
       /* ... */
       dirp = opendir(name); /* Opening directory for which os.listdir() was called */
       /* ... */



.. epigraph::

   The ``opendir()`` function opens a directory stream corresponding to the
   directory name, and returns a pointer to the directory stream. The stream
   is positioned at the first entry in the directory.

   -- Linux ``opendir()`` man page

.. code-block:: c

    /* continuing posix_listdir() */
    /* ... */
    for (;;) {
        ep = readdir(dirp); /* A crucial readdir() call */
        /* ... */
        /* ... */

        if (ep->d_name[0] == '.' && /* skipping '.' and '..' */
            (NAMLEN(ep) == 1 ||
             (ep->d_name[1] == '.' && NAMLEN(ep) == 2)))
            continue;
        if (arg_is_unicode)
            v = PyUnicode_DecodeFSDefaultAndSize(ep->d_name, NAMLEN(ep));
        else
            v = PyBytes_FromStringAndSize(ep->d_name, NAMLEN(ep));
        if (v == NULL) {
            Py_CLEAR(d);
            break;
        }
        if (PyList_Append(d, v) != 0) { /* appending found path to the return list */
            Py_DECREF(v);
            Py_CLEAR(d);
            break;
        }
        /* ... */
    }


.. epigraph::

   The ``readdir()`` function returns a pointer to a dirent structure
   representing the next directory entry in the directory stream pointed
   to by dirp. It returns NULL on reaching the end of the directory stream
   or if an error occurred.

   -- Linux ``readdir()`` man page

In Linux, the dirent structure is defined as follows:

.. code-block:: c

  struct dirent {
     ino_t          d_ino;       /* inode number */
     off_t          d_off;       /* offset to the next dirent */
     unsigned short d_reclen;    /* length of this record */
     unsigned char  d_type;      /* type of file; */
     char           d_name[256]; /* filename */
  };


As you can see, ``readdir()`` loops through a list of dirent structures,
and there is no quarantie that the structures will be somehow sorted.

So, how one can act when a sorted ``os.listdir()`` behaviour is required?
Pretty simple:


.. code-block:: python

  lst = sorted(os.listdir(path))

  # sorted files only
  files = sorted(f for f in os.listdir(path)
                 if os.path.isfile(os.path.join(path, f)))

  # sorted dirs only
  dirs = sorted(d for d in os.listdir(path)
                if os.path.isdir(os.path.join(path, d)))


Another Python mystery revealed!
