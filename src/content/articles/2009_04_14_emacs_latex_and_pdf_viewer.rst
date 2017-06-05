Emacs, LaTeX and pdf viewer
===========================

:slug: emacs_latex_and_pdf_viewer
:date: 2009-04-14 12:00
:category: Articles
:tags: Elisp, Emacs, LaTeX
:summary: A short note on how-to set a pdf-viewer for LaTeX-generated documents in Emacs.

My favourite editor Emacs provides a great support for LaTeX document
preparation system. There are several modes that extend the default
latex-mode. My favourite ones are: AUCTex (with Preview-latex) and CDLaTeX.

By-default LaTeX outputs DVI files and uses xdvi viewer with "View" command.
However it's possible to configure LaTeX to outpud pdf files. In Emacs,
you have to execute (``M-x tex-pdf-mode``) command to set the LaTeX's output
to pdf. If you'd like to have a pdf output for all LaTeX documents, add

.. code-block:: common-lisp

  (setq TeX-PDF-mode t)

to your ``.emacs``.

Now, let's add a pdf-viwer to be executed on "View" command (``C-c C-v``).
I use GNOME's default Evince document viewer for pdf files. So, the code that
should be added to .emacs is:

.. code-block:: common-lisp

  (defun pdfevince ()
     (add-to-list 'TeX-output-view-style
                   '("^pdf$" "." "evince %o %(outpage)")))

  (add-hook  'LaTeX-mode-hook  'pdfevince  t) ; AUCTeX LaTeX mode

That's it!
