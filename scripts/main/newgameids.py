"""This module scrapes for mlb game ids using the current date"""

from datetime import datetime, timedelta
from re import findall, compile as generate
import sys
sys.path.append('../utils')
from db import DB
from browsermanager import BrowserManager
from browserprocess import BrowserProcess

class Gameids(BrowserProcess):
	"""This class scrapes the mlb.com website for gameids using date input"""
	url = 'https://www.mlb.com/scores/{}'
	delay = 5

	def scrape(self):
		self.data['gameids'] = []
		self.data['gameids'] += [
			findall(r'[0-9]+', x['href'])[0]
			for x in self.soup(href=generate(r'https://www.mlb.com/gameday/[0-9]+/final/wrap'))
		]

	def post(self):
		with DB() as db:
			db.addgameids(self.data['gameids'], int(self.arg[0][:4]))
			new = db.getmissing(int(self.arg[0][:4]))
		print(f"Added {len(new)} games")

	def next(self):
		pass

if __name__ == '__main__':
	# yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
	# a = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
	# b = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
	# c = (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d')
	terms = [[(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d')]
			for x in range(15, 20)]
	# terms = [[yesterday], [a], [b], [c]]
	BrowserManager(Gameids, terms, 1, 5, False).run()
