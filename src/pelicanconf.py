import os

MYDIR = os.path.dirname(__file__)


AUTHOR = "Zaur Nasibov"
AUTHORS = {}
SITENAME = "Zaurun Fikirləri"
SITEDESCRIPTION = "Zaur's Thoughts"
SITELOGO = '/images/logo.png'
FAVICON = '/images/favicon.png'
COPYRIGHT_YEAR = 2017

CUSTOM_CSS = '/static/css/extra.css'

SITETITLE = "Zaurun Fikirləri"
SITESUBTITLE = "Zaur's Thoughts"

PATH = 'content'

ARTICLES_PATH = ['articles']

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

DISPLAY_PAGES_ON_MENU = True
DISPLAY_CATEGORIES_ON_MENU = True

MAIN_MENU = True

MENUITEMS = (
    ('Archives', '/archives.html'),
    ('Tags', '/tags.html'),
)

SOCIAL = (
    ('linkedin', 'https://www.linkedin.com/in/zaur-nasibov-44610853/'),
    ('github', 'https://github.com/basicwolf'),
    ('rss', '/feeds/atom.xml'),
)

DEFAULT_PAGINATION = 10

THEME = os.path.abspath(os.path.join(MYDIR, '../Flex/'))

STATIC_PATHS = ['images', 'attachments', 'static', 'extra/CNAME']

EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},}

PYGMENTS_RST_OPTIONS = {'linenos': 'table'}


ARTICLE_URL = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'
PAGE_URL = 'pages/{slug}/'
PAGE_SAVE_AS = 'pages/{slug}/index.html'

#PLUGINS_PATH = os.path.abspath(os.path.join(MYDIR, '../pelican-plugins'))
#PLUGIN_PATHS = [PLUGINS_PATH]
#PLUGINS = ["tag_cloud", "assets"]

# Blogroll
# LINKS = (('Pelican', 'http://getpelican.com/'),
#          ('Python.org', 'http://python.org/'),
#          ('Jinja2', 'http://jinja.pocoo.org/'),
#          ('You can modify those links in your config file', '#'),)
