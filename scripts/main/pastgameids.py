# pylint: disable=wrong-import-position
"""Scrapes mlb.com and inserts game, player, batter, and pitcher
information into database
"""
from re import findall
import sys
sys.path.append('../utils')
from db import DB
from browsermanager import BrowserManager
from browserprocess import BrowserProcess

class Gameids(BrowserProcess):
	"""Gameids inherites abstract class Browser_Thread. See Browser_Thread.__doc__."""
	url = 'https://www.mlb.com/{}/schedule/{}/fullseason'
	delay = 15

	def scrape(self):
		self.data['gameids'] = []
		for tr_ele in self.soup('tr', class_='primary-row-tr'):
			try:
				gameid = findall(
					'[0-9]+',
					tr_ele.find('td', class_='time-or-score-td-large').a['href']
				)[0]
				self.data['gameids'].append(gameid)
			except IndexError:
				pass

	def post(self):
		with DB() as db:
			db.addgameids(self.data['gameids'], self.arg[1])

if __name__ == '__main__':
	if len(sys.argv) == 1:
		print('\n\tUsage: {} <year>\n'.format(__file__))
		sys.exit()
	years = sys.argv[1:]
	with DB() as db:
		terms = [[x, y] for x in db.teamurls for y in years]
	BrowserManager(Gameids, terms, 5).run()
