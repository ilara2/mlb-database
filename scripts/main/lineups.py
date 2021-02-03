
from datetime import datetime, timedelta
from re import sub, compile as generate, findall
import sys
sys.path.append('../utils')
from browserprocess import BrowserProcess
from requestmanager import RequestManager
from player import Player
from db import DB

class Lineups(BrowserProcess):
	delay = 5
	url = 'https://www.mlb.com/starting-lineups/'
	# url = 'https://www.mlb.com/starting-lineups/2020-07-31'

	def scrape(self):
		date = self.soup.find('div', class_='starting-lineups__date-title').text.strip()
		date = sub(r'([0-9])..,', r'\1', date)
		self.data['date'] = datetime.strptime(date, '%B %d %Y').strftime('%Y-%m-%d')
		self.data['games'] = []
		self.getgames()

	def post(self):
		pass

	def next(self):
		pass

	def getgames(self):
		for card in self.soup('div', class_='starting-lineups__matchup'):
			try:
				game = self.setgame(card)
				[away_pit, home_pit] = self.setpitchers(card)
				bat_order = self.setorder(card)

				with DB() as db:
					db.addgame(*game[:3], self.data['date'])
					db.addgameid(game[0], self.data['date'].split('-')[0])

				ids = [x[0] for y in bat_order for x in y]
				ids += [away_pit, home_pit]
				with DB() as db:
					db_playerids = db.playerids()
				newids = []
				for playerid in ids:
					if playerid not in db_playerids:
						newids.append(playerid)
				if len(newids) > 0:
					tmp = [[x, game[0]] for x in newids]
					RequestManager(Player, tmp, 5).start()

				with DB() as db:
					[away_order, home_order] = db.addbatorder(bat_order)
				away_order.sort(key=lambda x: x[1])
				home_order.sort(key=lambda x: x[1])

				with DB() as db:
					db.addlineup(game[0], game[2], away_pit, *[x[0] for x in away_order])
					db.addlineup(game[0], game[1], home_pit, *[x[0] for x in home_order])
			# TODO
			#		- FIX ERROR!!!
			except Exception as e:
				print(e)
				continue

	@classmethod
	def setorder(self, card):
		[away, home] = card.find('div', class_='starting-lineups__teams')('ol')
		away_id = [int(findall(r'[0-9]+', li.find('a')['href'])[0]) for li in away('li')]
		away_pos = [x.text.strip().split(') ')[-1] for x in away('li')]
		home_id = [int(findall(r'[0-9]+', li.find('a')['href'])[0]) for li in home('li')]
		home_pos = [x.text.strip().split(') ')[-1] for x in home('li')]
		for i, pos in enumerate(away_pos):
			if pos[-1] == 'F':
				away_pos[i] = 'OF'
			elif pos == '1B':
				away_pos[i] = 'B1'
			elif pos == '2B':
				away_pos[i] = 'B2'
			elif pos == '3B':
				away_pos[i] = 'B3'
		for i, pos in enumerate(home_pos):
			if pos[-1] == 'F':
				home_pos[i] = 'OF'
			elif pos == '1B':
				home_pos[i] = 'B1'
			elif pos == '2B':
				home_pos[i] = 'B2'
			elif pos == '3B':
				home_pos[i] = 'B3'
		return [list(zip(away_id, away_pos)), list(zip(home_id, home_pos))]

	@classmethod
	def setpitchers(self, card):
		pitcher = card.find('div', class_='starting-lineups__pitchers')
		[away_pit, home_pit] = pitcher.div('div', recursive=False)[::2]
		away_pitcher = findall(
			r'[0-9]+',
			away_pit.find('a', href=generate(r'/player/.*[0-9]+'))['href']
		)[0]
		home_pitcher = findall(
			r'[0-9]+',
			home_pit.find('a', href=generate(r'/player/.*[0-9]+'))['href']
		)[0]
		return [int(away_pitcher), int(home_pitcher)]

	@classmethod
	def setgame(cls, card):
		gameid = card['data-gamepk']
		game = card.find('div', class_='starting-lineups__game')
		[away, home] = [x.text.strip() for x in game.div('span')[::2]]
		with DB() as db:
			awayid = db.teamid(away)
			homeid = db.teamid(home)
		# time = game.find('div', class_='starting-lineups__game-date-time').text
		# time = sub(r'\s+', ' ', time)
		# time = (datetime.strptime(time.strip(), '%I:%M %p') - timedelta(hours=3))\
		# 	.strftime('%I:%M %p')
		# if 'PPD' in time:
		# 	raise Exception()
		# return [gameid, homeid, awayid, time]
		return [gameid, homeid, awayid, 'LATER']

if __name__ == '__main__':
	from browsermanager import BrowserManager
	terms = [[]]
	BrowserManager(Lineups, terms, 1, 1, False).run()
