Blogging with Pelican
#####################

:date: 2017-04-25 21:00
:tags: blogging, pelican, python
:category: Articles
:slug: blogging-with-pelican
:summary: `Pelican <https://getpelican.com>`_ is a perfect blogging platform for programmers and computer geeks. My blog has been powered by Pelican for three years and it has been a pleasant experience. If you are looking forward to start a blog, or just thinking of changing a platform, why not give it a try?

`Pelican <https://getpelican.com>`_ is a static site generator,
that requires no database or server-side logic.
It is also an amazing blogging platform and as of April 2017,
my blog is powered by Pelican.
At this point, people stare at me with "*ORLY?*" expression on their faces.
Why not Wordpress, Tumblr, Facebook or any other 3rd-party blogging platform?

I tried Google Blogger a decade ago. Back then, the editor
was extremely basic and sometimes one had to edit HTML manually
to get the required visual representation.
Then there was Wordpress. It was rather nice, with all its integrated
features and thousands of free themes and plugins.
However, self-hosted Wordpress can be a painful experience.
Even with automatic updates I ended up with hacked blog
sending spam emails in background.


Around 2010 I wrote a simple blogging engine in Python/Django.
That was a nice programming exercise (you've got to try
it at least once in a lifetime!) but it required even more
maintenance: upgrading Django, fixing bugs, adding new features,
fixing styles in theme etc.

Free time was becoming luxury, so I started looking for
a solution which would take care of all the routine, which requires little or
no maintenance at all and which would be preferably written in a familiar
programming language.

`Tinkerer <http://tinkerer.me/>`_ was the first static blog generator
I encountered. It works fine,
however there are some configuration limitations e.g. the output
files and directory structure is generated in a certain hard-coded way.
Pelican on the other hand has a very wide range of configurable options
and provides great extensibility API for developers. As of April 2017
there are over 120 various 3rd-party plugins and over
100 user-made themes.
Needless to say, Pelican has a large and active community!

That is something one might expect from a good blogging platform.
Is there something what makes blogging via Pelican a remarkable experience
for computer geeks?

For starters, you write the content in `reStructuredText <http://docutils.sourceforge.net/rst.html>`_,
`Markdown <http://daringfireball.net/projects/markdown/>`_,
or `AsciiDoc <http://www.methods.co.nz/asciidoc/>`_  formats (btw, this blog is written in reStructuredText).
The code highlight comes right out of the box. You can publish the content in different languages.
You can even have multiple authors in a blog!
*Static* output means, that there is very little or no maintenance and
no more blog engine upgrades because of yet-another-critical-security-issue.
Thanks to the community, I don't have to worry about the themes and
once the static output is generated, it can be published literally anywhere, on any web server.

So begins the new era of my blog. Powered by Pelican!

P.S.

Thanks to Alexandre Vicenzi for `Flex <https://github.com/alexandrevicenzi/flex>`_ theme!
