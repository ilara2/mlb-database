
import sys
sys.path.append('../utils')
from db import DB
from browser import *
url = 'https://www.reddit.com'
browser = Browser('../chromedriver.exe', 1, True)
browser.windows[0].get(url)
browser.windows[0].get('https://www.mlb.com/scores/2020-07-23')
browser.windows[0].get('https://www.mlb.com/scores/2020-07-23')
browser.windows[0].get('https://www.mlb.com/scores/2020-07-23')
soup = browser.windows[0].page_source
soup.title
soup.title()
from bs4 import beautifulsoup4 as bs
from bs4 import BeautifulSoup as bs
soup = bs(soup, 'html.parser')
soup.title
soup.title.text
import re
soup(href=re.compile(r'https://www.mlb.com/gameday/[0-9]+/final/wrap'))
links = soup(href=re.compile(r'https://www.mlb.com/gameday/[0-9]+/final/wrap'))
links[0]['href']
links = [re.findall(r'[0-9]+', x['href']) for x in soup(href=re.compile(r'https://www.mlb.com/gameday/[0-9]+/final/wrap'))]
links
links = [re.findall(r'[0-9]+', x['href'])[0] for x in soup(href=re.compile(r'https://www.mlb.com/gameday/[0-9]+/final/wrap'))]
links
browser.windows[0].get('https://www.mlb.com/scores/2020-07-24')
soup = bs(browser.windows[0].page_source, 'html.parser')
links = [re.findall(r'[0-9]+', x['href'])[0] for x in soup(href=re.compile(r'https://www.mlb.com/gameday/[0-9]+/final/wrap'))]
links
len(links)
