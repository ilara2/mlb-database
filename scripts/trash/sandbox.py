"""Junk Yard"""

import sys
sys.path.append('../utils')
from db import DB
from browser import *

url = 'https://www.reddit.com'
browser = Browser('../chromedriver.exe', 1, True)
browser.windows[0].get(url)
