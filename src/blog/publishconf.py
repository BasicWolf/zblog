# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

# If your site is available via HTTPS, make sure SITEURL begins with https://
SITEURL = 'https://zaurnasibov.com'
RELATIVE_URLS = False

FEED_ALL_ATOM = 'feeds/all.atom.xml'
FEED_DOMAIN = SITEURL


DELETE_OUTPUT_DIRECTORY = True

CACHE_CONTENT = False

SITEURL = "https://www.zaurnasibov.com/"

SIMPLE_COMMENTS = False
