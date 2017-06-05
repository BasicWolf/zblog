import os
import sys
sys.path.append(os.curdir)

from pelicanconf import *

SITEURL = 'http://znasibov.info'
RELATIVE_URLS = False

# MENUITEMS = ((name, SITEURL + url) for name, url in MENUITEMS)

FEED_DOMAIN = 'znasibov.info'
FEED_ATOM = 'feeds/atom.xml'

DELETE_OUTPUT_DIRECTORY = True
# OUTPUT_PATH = os.path.expanduser('~/webapps/zblog4')

DISQUS_SITENAME = 'znasibov'
FACEBOOK_API = True
GOOGLE_ANALYTICS = 'UA-9017911-1'
