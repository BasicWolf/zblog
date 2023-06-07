The curious case of denied repository access in Github Actions workflow
#######################################################################

:slug: the-curious-case-of-denied-repository-access-in-github-actions-workflow
:category: Articles
:tags: programming, blog, pelican, git, github, actions, ci/cd, access denied
:date: 2024-06-01 22:59
:status: published
:summary:
   .. image:: {static}the-curious-case-of-denied-repository-access-in-github-action.rst.png
      :width: 100%
      :align: center
      :alt: Intro image for the article
      :target: {filename}the-curious-case-of-denied-repository-access-in-github-action.rst

   While configuring a continuous delivery pipeline for this blog,
   I encountered unexpected permission denials from GitHub.
   Was there something wrong with the setup?

.. image:: {static}the-curious-case-of-denied-repository-access-in-github-action.rst.png
   :width: 100%
   :align: center
   :alt: Intro image for the article

*GitHub Pages* is a fantastic static site hosting service that takes HTML, CSS,
and JavaScript files straight from a repository on GitHub. It is available for
free on public repositories and allows configuring a custom domain for the site.
The site updates just in few moments after ``git push``.
Therefore, when it comes to choosing a platform for hosting a static blog,
opting for GitHub is an obvious choice.

There are
`three types <https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages#types-of-github-pages-sites>`_
of GitHub Pages sites: *project*, *user* and *organisation*.
To publish a user site to ``https://<username>.github.io``, you have to create
a repository with the same name. By default, the site is served from the
master branch and the root of the repository.

My blog is written in
`reStructuredText (reST) <https://en.wikipedia.org/wiki/ReStructuredText>`_
format and compiled into a static site via
`Pelican <https://docs.getpelican.com/en/latest/>`_.
I keep the source of the blog in a separate private repository called (surprise!) "blog."
The built blog site is deployed to ``basicwolf.github.io`` via force-pushing,
so there is only a single branch with a single commit in the repository.
The whole setup allows me to hide intermediate work and expose only the end result to the public.

For years I've been manually publishing the blog from my computer
- a paradoxical situation considering my longstanding advocacy
for continuous integration and delivery.
Even my other hobby projects incorporate a CI/CD pipeline in some form or another.
Finally, the time has come to set up a pipeline for the blog, and fortunately,
in the year 2023, GitHub Actions have shown to be highly effective and efficient
in getting the job done.

I set up the pipeline as follows:
when a push occurs on the master branch of the ``blog`` repository, an action is triggered.
This action builds the website, commits the resulting changes to the ``gh-pages`` branch,
and pushes the branch to the ``basicwolf.github.io:master`` repository.

.. image:: {static}publish-from-one-repo-to-another.svg
   :width: 90%
   :align: center
   :alt: Publishing from blog repository to basicwolf.github.io repository


At this point, things became a little complicated. The workflow runs
within the ``blog`` repository context but pushes the results (i.e. the site)
to the ``basicwolf.github.io`` repository. To accomplish this I had to utilize
a dedicated personal access token (PAT) for the second repository, granting it
*Read and Write access to code* permissions.
The token was subsequently utilized in the following manner:

::

   git push -f https://basicwolf:${MY_TOKEN}@github.com/BasicWolf/basicwolf.github.io.git gh-pages:master

I generated a PAT and tested it by pushing the site from my computer.
Everything went smoothly, and I was looking forward to quickly complete the workflow setup.
Little did I know that I would be banging my head against the keyboard for two days,
trying to comprehend ``git push`` permissions denials.

I pushed the workflow file and began monitoring its maiden voyage.
Everything was running smoothly until the final step - pushing the site to ``basicwolf.github.io``:

::

   git push -f ***github.com/BasicWolf/basicwolf.github.io.git gh-pages:master
   remote: Permission to BasicWolf/basicwolf.github.io.git denied to github-actions[bot].
   fatal: unable to access 'https://github.com/BasicWolf/basicwolf.github.io.git/': The requested URL returned error: 403

I won't burden you with the details of verifying that the token remained intact during the ``git push`` process.
Whether it involved checking its length, echoing token fragments, or generating new tokens,
the token itself was sure present in the workflow.
However, despite its presence, access was denied when attempting to push from the workflow run,
while it was granted when pushing from my computer.

I began suspecting that an internal authorization mechanism was to blame here.
However, the question remained: which one? Fortunately, the
`checkout action <https://github.com/marketplace/actions/checkout>`_
includes comprehensive logging and provides a clue in the "Setting up auth" section:

::

   Setting up auth
     /usr/bin/git config --local --name-only --get-regexp core\.sshCommand
     ...
     /usr/bin/git config --local http.https://github.com/.extraheader AUTHORIZATION: basic ***

Aha! The checkout action configures authorization by setting HTTP Authorization header in  git's ``http.extraheader``:

..

   **http.extraHeader**
     Pass an additional HTTP header when communicating with a server. If more than one such entry exists, all of them are added as extra headers. To allow overriding the settings inherited from the system config, an empty value will reset the extra headers to the empty list. `[source] <https://git-scm.com/docs/git-config/2.41.0#Documentation/git-config.txt-httpextraHeader>`_

What if I read the documentation for the checkout action?

..

   The auth token is persisted in the local git config.
   This enables your scripts to run authenticated git commands.
   The token is removed during post-job cleanup .

The action includes a ``token`` parameter that has a default value of ``${{ github.token }}!``
This token is equivalent to ``GITHUB_TOKEN`` - a unique token generated by Github at the start of each workflow run.
However, it is important to note that this token is restricted to the repository where the workflow is executed.

Finally, all the pieces of the puzzle fell into place.
What I required was a PAT with read access to the blog source repository
and write access to ``basicwolf.github.io``.
Once generated, I passed this PAT to the checkout action as follows:

::

   steps:
     - uses: actions/checkout@v3
       with:
         token: ${{secrets.ACCESS_TOKEN_BASICWOLF_GITHUB_IO}}

There is no need to explicitly provide the token for git push anymore,
as the git configuration remains consistent across the steps.

This marked the end of an epic quest.
The workflow pipeline successfully passed, and you have just completed reading
the first article that was automatically deployed to this blog :).
