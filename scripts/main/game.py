# pylint: disable=wrong-import-position, bad-continuation, consider-using-enumerate, invalid-name
"""Scrapes mlb.com and inserts game, player, batter, and pitcher
information into database
"""
from datetime import datetime
from re import findall, sub
from multiprocessing import Lock
import sys
sys.path.append('../utils')
from db import DB
from requestmanager import RequestManager
from browserprocess import BrowserProcess
from player import Player
from errors import GameRecordError
from atbats import AtBats

# TODO
#		- Error handling whenever I access the soup
#		- Move all post to an individual method
#		- Scrape time for games
#		- inserts into db.games may be move to lineup.py and remove from here
#		- scrape game time start

class Game(BrowserProcess):
	"""Game inherites abstract class BrowserProcess. See BrowserProcess.__doc__.
	Captures game, player, batter and pitcher stats in that order.
	"""
	url = 'https://www.mlb.com/gameday/{0}#game_state=final,game_tab=box,game={0}'
	delay = 5

	def scrape(self):
		self.data['gameid'] = self.arg[0]
		self.setgame()
		self.getplayerids()
		self.setplayers()
		self.setbatterstats()
		self.setpitcherstats()

	def post(self):
		pass

	def next(self):
		tmp_lock = self.window.lock
		self.window.lock = Lock()
		p = AtBats([self.data['gameid']], self.window)
		p.seturl(sub(
			r'(game_tab=)([a-z_]+),',
			r'\1play-by-play,',
			self.window.current_url))
		p.start()
		p.join()
		self.window.lock = tmp_lock

	def setgame(self):
		"""Scrapes and inserts game info into database"""
		title = self.soup.title.text
		try:
			[match, date] = title.split(' Box Score | ')
		except ValueError as e:
			print(e)
			print(self.data['gameid'])
		[away, home] = match.split(' vs. ')
		date = datetime.strptime(date, '%m/%d/%y').strftime('%Y-%m-%d')
		if not (away and home and date):
			raise GameRecordError(self.data['gameid'])
		time = [sub('First pitch: ', '', x.text)[:-1]
			for x in self.soup('section', class_='box game')[0].div('div', recursive=False)
			if x.span.text == 'First pitch'][0]
		time = datetime.strptime(time, '%I:%M %p').strftime('%H:%M')
		with DB() as db:
			self.data['awayid'] = db.teamid(away)
			self.data['homeid'] = db.teamid(home)
			# print(self.data['gameid'], self.data['homeid'], self.data['awayid'], date, time)
			db.addgame(self.data['gameid'], self.data['homeid'], self.data['awayid'], date, time)

	def getplayerids(self):
		"""Returns a list of playerid ints"""
		self.data['playerids'] = []
		# Batters' id
		for link in [span.a for span in self.soup('span', class_='name')]:
			self.data['playerids'].append(int(findall('[0-9]+', link['href'])[0]))
		# Pitchers' id
		for link in [link for sect in self.soup('section', class_='pitching') for link in sect('a')]:
			self.data['playerids'].append(int(findall('[0-9]+', link['href'])[0]))

	def setplayers(self):
		"""Inserts player info into database"""
		with DB() as db:
			db_playerids = db.playerids()
		newids = []
		for playerid in self.data['playerids']:
			if playerid not in db_playerids:
				newids.append(playerid)
		if len(newids) > 0:
			tmp = [[x, self.data['gameid']] for x in newids]
			RequestManager(Player, tmp, 5).start()

	@classmethod
	def _sortBatTable(cls, row):
		playerid = int(findall('[0-9]+', row.a['href'])[0])
		name = row.a.text
		if name[1] == '-':
			name = name[2:]
		# [ab, r, h, rbi, bb, so]
		stats = [int(stat.text) for stat in row('td')[1:7]]
		return [name, playerid] + stats[:3] + [0, 0, 0] + stats[3:]

	@classmethod
	def _sortDets(cls, row):
		tmp = row.text.replace(row.span.text, '')[2:]
		names = sub(r'\([^\)]*\)', '', tmp)[:-1].split(';')
		num = [(findall('[0-9]+', name) or [1]) for name in names]
		num = [int(x[0]) for x in num]
		names = [sub('[0-9]+', '', name) for name in names]
		names = [name.strip() for name in names]
		return [names, num]

	def setbatterstats(self):
		# pylint: disable= too-many-branches,too-many-locals
		"""Set batters' stats"""
		data = dict()
		data['home'] = []
		data['away'] = []
		[bat_away, bat_home] = self.soup('section', class_='batting')
		table_away = bat_away.table.tbody
		table_home = bat_home.table.tbody
		dets_away = [div for div in bat_away('div', recursive=False) if div.span][0]
		dets_home = [div for div in bat_home('div', recursive=False) if div.span][0]

		# # Basic Stats
		# #Away
		for row in table_away('tr')[:-1]:
			stats = self._sortBatTable(row)
			stats.insert(1, self.data['gameid'])
			stats.insert(2, self.data['awayid'])
			data['away'].append(stats)
		# #Home
		for row in table_home('tr')[:-1]:
			stats = self._sortBatTable(row)
			stats.insert(1, self.data['gameid'])
			stats.insert(2, self.data['homeid'])
			data['home'].append(stats)
		# # Stat Details
		# # Away
		for row in dets_away('div'):
			#
			# GOTTA CHANGE IDX BY +2
			#
			if row.span.text == '2B':
				idx = 5+2
			elif row.span.text == '3B':
				idx = 6+2
			elif row.span.text == 'HR':
				idx = 7+2
			else:
				continue
			[names, num] = self._sortDets(row)
			for i in range(len(names)):
				for j in range(len(data['away'])):
					if names[i] == data['away'][j][0]:
						data['away'][j][idx] += num[i]
		# # Home
		for row in dets_home('div'):
			#
			# GOTTA CHANGE IDX BY +2
			#
			if row.span.text == '2B':
				idx = 5+2
			elif row.span.text == '3B':
				idx = 6+2
			elif row.span.text == 'HR':
				idx = 7+2
			else:
				continue
			[names, num] = self._sortDets(row)
			for i in range(len(names)):
				for j in range(len(data['home'])):
					if names[i] == data['home'][j][0]:
						data['home'][j][idx] += num[i]
		data = data['away']+data['home']
		for row in data:
			del row[0]
		self.data['batterstats'] = data
		with DB() as myDB:
			myDB.addbatterstats(data)

	@classmethod
	def _sortPitTable(cls, row):
		playerid = int(findall('[0-9]+', row.a['href'])[0])
		name = row.a.text.replace(row.a.span.text, ' ').strip()
		if name[1] == '-':
			name = name[2:]
		ip = float(row('td')[1].text)
		[h, r, er, bb, so, hr] = [int(stat.text) for stat in row('td')[2:8]]
		return [name, playerid, ip, h, r, er, hr, bb, so, 0, 0, 0, 0]

	@classmethod
	def _sortPIT(cls, row):
		tmp = row.text.replace(row.span.text, '')[2:]
		names = sub(r'\([^\)]*\)', '', tmp)[:-1].split(';')
		num = [findall('[0-9]+-[0-9]+', name)[0].split('-') for name in names]
		num = [int(x[0]) for x in num]
		names = [sub('[0-9]+-[0-9]+', '', name) for name in names]
		names = [name.strip() for name in names]
		return [names, num]

	@classmethod
	def _sortGBFB(cls, row):
		tmp = row.text.replace(row.span.text, '')[2:]
		names = sub(r'\([^\)]*\)', '', tmp)[:-1].split(';')
		num = [findall('[0-9]+-[0-9]+', name)[0].split('-') for name in names]
		names = [sub('[0-9]+-[0-9]+', '', name) for name in names]
		names = [name.strip() for name in names]
		return [names, num]

	def setpitcherstats(self):
		# pylint: disable= too-many-branches
		"""Sets pitchers' stats"""
		data = []
		[pit_away, pit_home] = self.soup('section', class_='pitching')
		table_away = pit_away.table.tbody
		table_home = pit_home.table.tbody
		dets = [div for div in self.soup('div', class_='info gd-primary-regular') if div.span][0]
		dets = self.soup('section', class_='box game')[0].div
		# Basic Stats
		#Away
		for row in table_away('tr')[:-1]:
			stats = self._sortPitTable(row)
			stats.insert(1, self.data['gameid'])
			stats.insert(2, self.data['awayid'])
			data.append(stats)

		#Home
		for row in table_home('tr')[:-1]:
			stats = self._sortPitTable(row)
			stats.insert(1, self.data['gameid'])
			stats.insert(2, self.data['homeid'])
			data.append(stats)

		for row in dets('div'):
			if row.span.text == 'Pitches-strikes':
				[names, num] = self._sortPIT(row)
				idx = 11+2
				for i in range(len(names)):
					for j in range(len(data)):
						if names[i] == data[j][0]:
							data[j][idx] += int(num[i])
			elif row.span.text == 'Groundouts-flyouts':
				[names, num] = self._sortGBFB(row)
				idx = 9+2
				for i in range(len(names)):
					for j in range(len(data)):
						if names[i] == data[j][0]:
							data[j][idx] += int(num[i][0])
							data[j][idx+1] += int(num[i][1])
			elif row.span.text == 'Batters faced':
				[names, num] = self._sortDets(row)
				idx = 12+2
				for i in range(len(names)):
					for j in range(len(data)):
						if names[i] == data[j][0]:
							data[j][idx] += int(num[i])
			else:
				continue
		for row in data:
			del row[0]
		self.data['pitcherstats'] = data
		with DB() as myDB:
			myDB.addpitcherstats(data)

if __name__ == '__main__':
	from browsermanager import BrowserManager
	if len(sys.argv) != 2:
		print('\nUsage: python3 game.py <year, year, ...>\n')
		sys.exit(0)
	else:
		year = sys.argv[1]
	with DB() as db:
		terms = db.getmissing(year)
	BrowserManager(Game, terms, 3, 5, False).run()
