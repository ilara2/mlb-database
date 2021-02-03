"""Custom Errors"""

class PageNotLoaded(Exception):
	"""Error when the page is not fully loaded and missing attributes"""
	def __init__(self, playerid, gameid):
		super().__init__('Player {} did not load correctly.'.format(playerid))
		self.playerid = playerid
		self.gameid = gameid
		tmp = 'gameid: {:<7}\tplayerid: {:<10}\n'\
				.format(self.gameid, self.playerid)
		with open('../errors/PageNotloaded.log', 'a') as file:
			file.write(tmp)

class GameRecordError(Exception):
	"""Temp Error"""
	def __init__(self, gameid):
		self.msg = 'gameid: {}\n'\
				.format(gameid)
		super().__init__(self.msg)
		with open('../errors/GameRecordError.log', 'a') as file:
			file.write(self.msg)

class PitcherNotFound(Exception):
	"""Error when a pitcher's name from mlb's pitch sequance is not found in the database"""
	def __init__(self, gameid: int, player: str, inn: int):
		self.msg = 'gameid: {:<7}\tinning: {:<2}\tplayer: {:<}\n'\
				.format(gameid, inn, player)
		super().__init__(self.msg)
		with open('../errors/PitcherNotFound.log', 'a') as file:
			file.write(self.msg)

class LeftOverPitchers(Exception):
	"""Error when a pitcher's name from mlb's pitch sequance is not found in the database"""
	def __init__(self, gameid: int, pitchers: list):
		self.msg = 'gameid: {}\n'\
				.format(gameid)
		for row in pitchers:
			self.msg += '\tplayerid: {:<7}\tname: {:<}\n'.format(row[1], row[0])
		super().__init__(self.msg)
		with open('../errors/LeftOverPitchers.log', 'a') as file:
			file.write(self.msg)
		