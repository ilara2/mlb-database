"""A postgres wrapper"""
from re import sub
import psycopg2

# TODO
#		- seperate queries for 'selects' and 'inserts'
class DB():
	"""Connects to local psql database and provide helper functions"""
	def __init__(self):
		conn_str = """
			host=localhost
			port=5432
			dbname=mlb_bak
			user=ilara
			password=temp_passwd
		"""
		self.conn = psycopg2.connect(conn_str)
		self.conn.autocommit = True
		self.cur = self.conn.cursor()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		"""Clean up"""
		self.conn.close()
		del self.cur
		del self.conn
		del self

	def cleantable(self):
		"""Delets from temp tables"""
		# self.cur.execute('delete from pitchseq')
		# self.cur.execute('delete from atbats')
		# self.cur.execute('delete from batterstats')
		# self.cur.execute('delete from pitcherstats')
		# self.cur.execute('delete from games')

	def query(self, text: str, var: list =None) -> list:
		"""Queries the database and returns results.
		*text* query for database
		"""
		self.cur.execute(text, var)
		if self.cur.rowcount:
			return self.cur.fetchall()
		return []

	def select(self, text: str, var: list =None) -> list:
		"""Queries the database and returns results.
		*text* query for database
		"""
		self.cur.execute(text, var)
		if self.cur.rowcount:
			return self.cur.fetchall()
		return []

	def insert(self, text: str, var: list =None) -> list:
		"""Inserts into database
		"""
		self.cur.execute(text, var)
		return

	def returning(self, text: str, var: list =None) -> list:
		"""Queries the database and returns results.
		*text* query for database
		"""
		self.cur.execute(text, var)
		if self.cur.rowcount:
			return self.cur.fetchall()
		return []

	def querymany(self, text: str, arr: list) -> list:
		"""Queries the database and returns results.
		*text* query for database
		"""
		self.cur.executemany(text, arr)
		if self.cur.rowcount > 0:
			return self.cur.fetchall()
		return []

	#
	# gameids.py
	#
	@property
	def teamurls(self) -> list:
		"""Returns list of MLB's teams' short hand."""
		return [
			x[0]
			for x in self.select('select short_name from teams order by random()')
		]

	def addgameids(self, gameids: list, year: int) -> None:
		"""Inserts into database records of games' ids.
		*gameids* list of games' ids to be added.
		*year* the year the games where played.
		"""
		query = 'insert into gameids values'
		for gameid in gameids:
			query += ' ({}, {}),'.format(gameid, year)
		query = query[:-1] + ' on conflict do nothing;'
		self.insert(query)

	def addgameid(self, gameid: int, year: int) -> None:
		"""Inserts a single gameid into db.gameids
		*gameids* list of games' ids to be added.
		*year* the year the games where played.
		"""
		query = f'insert into gameids values ({gameid}, {year}) on conflict do nothing'
		self.insert(query)

	#
	# game.py
	#
	def getgameids(self, years: list, rand: bool = True) -> list:
		"""Returns game ids of games played during years"""
		query = 'select gameid from gameids where'
		query += ' year={} or' * (len(years) - 1)
		query += ' year={}'
		if rand:
			query += ' order by random()'
		query = query.format(*years)
		return [x[:1] for x in self.select(query)]

	def playerids(self) -> list:
		"""Returns player ids from database"""
		return [x[0] for x in self.select('select playerid from players')]

	def teamid(self, name: str) -> int:
		"""Returns team's id.
		*name* is short hand for a teams' name.
		"""
		ret = self.select("""
			select teamid
			from teams
			where lower(url_name) like lower('%{0}%')
			or lower(name) like lower('%{0}%')
		""".format(name))
		try:
			return ret[0][0]
		except IndexError:
			print()
			print(name)
			print(ret)
			print()

	def addgame(self, gameid: int, homeid: int, awayid: int, date: str, time: str = None) -> None:
		"""Inserts complete game record into database.
		*gameid* the game's id.
		*homeid* the home team's database id.
		*awayid* the away team's database id.
		*date* the date the game was played.
		*time* the time the game was played.
		"""
		query = "insert into games values ({}, {}, {}, '{}', '{}')"\
			.format(gameid, homeid, awayid, date, time)
		# query = "insert into games(gameid, homeid, awayid, date) values ({}, {}, {}, '{}')"\
		# 	.format(gameid, homeid, awayid, date, time)
		query += ' on conflict do nothing'
		self.insert(query)

	def getmissing(self, year: int):
		return self.select(f"""
			select a.gameid
			from gameids a
			full outer join games b
			on a.gameid=b.gameid
			where b is null
			and year={year}
		""")

	def geterrors(self):
		return self.select("""
			select b.gameid
			from gameids a
			full outer join games b
			on a.gameid=b.gameid
			where a is null
		""")
	#
	# player.py
	#
	def addplayer(self, args: list) -> None:
		"""Adds player information into database.
		*args* array containing [playerid, fname, mname, lname, fullname, position, DOB, bats, throws].
		"""
		# Escapes single quote for psql
		for i in range(1, 5):
			args[i] = sub("'", "''", args[i])
		if args[-3]:
			query = """
				insert into players
				values ({}, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
				on conflict do nothing
			""".format(*args)
		else:
			del args[-3]
			query = """
				insert into players
				values ({}, '{}', '{}', '{}', '{}', '{}', NULL, '{}', '{}')
				on conflict do nothing
			""".format(*args)
		self.insert(query)

	def addbatterstats(self, args: list) -> None:
		"""Adds batterstats into database"""
		query = """
			insert into batterstats values
		"""
		for row in args:
			query += " ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}),"\
				.format(*row)
		query = query[:-1] + ' on conflict do nothing;'
		self.insert(query)

	def addpitcherstats(self, args: list) -> None:
		"""Adds batterstats into database"""
		query = """
			insert into pitcherstats values
		"""
		for row in args:
			query += " ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}),"\
				.format(*row)
		query = query[:-1] + ' on conflict do nothing;'
		self.insert(query)
	#
	# atbats.py
	#
	def gameteams(self, gameid: int) -> list:
		"""Returns awayid and homeid for teams that played in game"""
		return self.select('select awayid, homeid from games where gameid={}'\
				.format(gameid))[0]

	def pitcherpergame(self, gameid: int) -> list:
		"""Returns pitchers that played in game"""
		return self.select("""
			select b.name, a.*
			from
				(select playerid, teamid
				from pitcherstats
				where gameid={}) a
			natural join players b
		""".format(gameid))

	def addatbat(self, stats: list) -> int:
		query = """
			insert into atbats(gameid, pitcherid, batterid, inn, num, action)
			values ({}, {}, {}, {}, {}, '{}') returning atbatid
		""".format(*stats)
		return self.returning(query)[0][0]

	def addpitch_seq(self, arr):
		if len(arr) == 0:
			return
		query = 'insert into pitchseq values'
		for row in arr:
			app = " ({}, {}, '{}', {}, '{}'),"
			if not row[2]:
				row[2] = 'null'
				app = " ({}, {}, {}, {}, '{}'),"
			if not row[3]:
				row[3] = 'null'
			query += app.format(*row)
		query = query[:-1]
		self.insert(query)
	#
	# lineups.py
	#
	def addbatorder(self, arr: list) -> list:
		""""""
		away = [(row[0], i+1) for i, row in enumerate(arr[0])]
		home = [(row[0], i+1) for i, row in enumerate(arr[1])]
		q = 'insert into batorder(playerid, order_num) values (%s, %s) '+\
			'on conflict(playerid, order_num) do update set order_num=excluded.order_num returning batorderid'
		away = [self.returning(q, x)[0][0] for x in away]
		away = list(zip(away, [x[1] for x in arr[0]]))
		home = [self.returning(q, x)[0][0] for x in home]
		home = list(zip(home, [x[1] for x in arr[1]]))
		return [away, home]

	def addlineup(self, gameid, teamid, pitcher,
			b1, b2, b3, c, dh, of1, of2, of3, ss):
		q = f"""insert into lineup values ({gameid}, {teamid}, {pitcher},
			{b1}, {b2}, {b3}, {c}, {dh}, {of1}, {of2}, {of3}, {ss})
			on conflict do nothing"""
		print(sub(r'\s+', ' ', q))
		self.insert(q)

	# def addgameid(self, gameid, year):
	# 	self.insert(f'insert into gameids values({gameid}, {year})')
