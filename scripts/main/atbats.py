# pylint: disable=wrong-import-position, redefined-outer-name, invalid-name
"""Scrapes mlb.com for players' atbats and pitchers' pitch sequence"""
from re import sub, compile
import sys
sys.path.append('../utils')
# from unidecode import unidecode
from db import DB
from browserprocess import BrowserProcess
from errors import LeftOverPitchers
from hamming import Hamming
# from json import dumps

# - BUG program inserts two data rows when there is an intentional walk
#			ex: gameid - 565230

class AtBats(BrowserProcess):
	"""AtBats inherites abstract class BrowserProcess. See BrowserProcess.__doc__.
	Captures atbat and pitch sequences info.
	"""
	url = 'https://www.mlb.com/gameday/{0}#game_state=final,game_tab=play-by-play,game={0}'
	delay = 2

	def scrape(self):
		self._setvariables()
		self._sortpitchers()
		self._sortinnings()

	def post(self):
		for row in self.data['atbats']:
			with DB() as db:
				atbatid = db.addatbat(row[0])
				for i in range(len(row[1])):
					row[1][i].insert(0, atbatid)
				db.addpitch_seq(row[1])

	def next(self):
		pass

	def _sortpitchseq(self, pitch_seq) -> list:
		"""Sorts pitches throw during at bat"""
		data = []
		pitch_seq = pitch_seq.div
		for pitch in pitch_seq('div'):
			if pitch.has_attr('class')\
					and 'pitch' in pitch['class']\
					and 'new' in pitch['class']\
					and 'clearfix' in pitch['class']:
				pit = pitch('div')
				num = pit[0].span.text
				if not num:
					continue
				outcome = pit[1].span.text
				tmp = pit[1].text.replace(outcome, '', 1).strip()
				if 'no-pitch-info' in pitch['class']:
					[speed, ptype] = ['', '']
				else:
					[speed, ptype] = tmp.split(' MPH ')
				data.append([
					num,
					ptype,
					speed,
					outcome
				])
		return data

	def _sortatbat(self, half, inn, pitchers):
		"""Reads a single atbat"""
		num = 1
		for div in half('div', recursive=False):
			if 'play' in div['class']:
				atbat = div('div', recursive=False)
				pitcherid = pitchers[0][1]
				try:
					batterid = atbat[0].find(
							'a', href=compile('https://www.mlb.com/player/[0-9]+')
					)['href'][-6:]
				except TypeError:
					continue
				action = atbat[0].find('div', class_='gd-info-event event').text
				stats = [self.data['gameid'], pitcherid, batterid, inn, num, action]
				self.data['atbats'].append([stats, []])
				num += 1
				pitch_seq = self._sortpitchseq(atbat[2])
				if len(pitch_seq) == 0 or 'Intent Walk' in stats[5]:
					continue
				self.data['atbats'][-1][1] = pitch_seq
			elif 'action' in div['class']:
				if div.h3 \
						and div.h3.text == 'Pitching Substitution' \
						and div.p.text[:17] == 'Pitching Change: ':
					del pitchers[0]

	def _sortinnings(self):
		"""Sorts innings by top and bottom half"""
		inns_soup = self.soup('div', class_='inning_tabs')
		for i in range(len(inns_soup)):
			[top, bot] = inns_soup[i]('section')
			self._sortatbat(top, i+1, self.data['homeordered'])
			self._sortatbat(bot, i+1, self.data['awayordered'])

		if len(self.data['homeordered']) > 1:
			raise LeftOverPitchers(self.data['gameid'], self.data['homeordered'])
		if len(self.data['awayordered']) > 1:
			raise LeftOverPitchers(self.data['gameid'], self.data['awayordered'])

	def order(self, half, pitchers, ordered):
		"""Sorts pitchers in order of appearance"""
		actions = half('div', class_='action')
		for action in actions:
			if action.h3 and action.h3.text == 'Pitching Substitution' and \
						action.p.text[:17] == 'Pitching Change: ':
				name = action.p.text.replace('Pitching Change: ', '').split(' replaces ')[0].strip()
				name = sub(r'\s+Jr\.\s*', '', name)
				name = sub(r'\s*(.)\.', r'\1', name)
				name = sub(r'\s+', r' ', name)
				name = name.strip()
				assert len(pitchers) != 0,\
						"gameid: {} - pitchers' list is empty".format(self.data['gameid'])
				closest = Hamming.closest(name, pitchers)
				ordered.append(closest)

	def _sortpitchers(self):
		"""Sort pitchers into correct order of appearance"""
		inns_soup = self.soup('div', class_='inning_tabs')
		for i in range(len(inns_soup)):
			[top, bot] = inns_soup[i]('section')
			self.order(top, self.data['homepitchers'], self.data['homeordered'])
			self.order(bot, self.data['awaypitchers'], self.data['awayordered'])

		t1 = [x for x in self.data['homepitchers'] if x not in self.data['homeordered']]
		t2 = [x for x in self.data['awaypitchers'] if x not in self.data['awayordered']]

		self.data['homeordered'].insert(0, t1[0])
		del self.data['homepitchers']
		self.data['awayordered'].insert(0, t2[0])
		del self.data['awaypitchers']

	def _setvariables(self):
		"""Sets up locl variables"""
		self.data['gameid'] = self.arg[0]
		with DB() as db:
			[self.data['awayid'], self.data['homeid']] = db.gameteams(self.data['gameid'])
			pitchers = db.pitcherpergame(self.data['gameid'])
		self.data['awaypitchers'] = list(filter(lambda x: x[2] == self.data['awayid'], pitchers))
		self.data['homepitchers'] = list(filter(lambda x: x[2] == self.data['homeid'], pitchers))
		self.data['awayordered'] = []
		self.data['homeordered'] = []
		self.data['atbats'] = []

	def seturl(self, url):
		"""Change the target url if needed"""
		self.url = url

if __name__ == '__main__':
	from browsermanager import BrowserManager
	with DB() as db:
		terms = db.getgameids([2019, 2020])
	BrowserManager(AtBats, terms, 1, 1).run()
	