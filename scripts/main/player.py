# pylint: disable=wrong-import-position, bad-continuation
"""sandbox file to test out code"""
from re import findall, sub
import sys
sys.path.append('../utils')
from requestmanager import RequestManager
from requestthread import RequestThread
from db import DB
from errors import PageNotLoaded

class Player(RequestThread):
	"""A class that scrapes player information from mlb.com and inserts it into database."""
	url = 'https://www.mlb.com/player/{0}'
	delay = 5

	def scrape(self):
		self.data['playerid'] = self.arg[0]
		self.data['gameid'] = self.arg[1]
		data = [self.data['playerid']]+self._getname()+self._getdeets()
		with DB() as my_db:
			my_db.addplayer(data)

	def _getname(self):
		try:
			name = self.soup.find('li', class_='full-name')
			fullname = name.text.replace(name.span.text, '').strip()
			listname = self.soup.find('span', class_='player-header--vitals-name').text
			listname = listname.replace(' Jr.', '')
			sep = findall(r"[\w']+(?: Jr.)?", fullname)
			fname = sep[0]
			lname = sep[-1]
			mname = ''
			if len(sep) > 2:
				mname = sep[1]
				lname = ' '.join(sep[2:])
			data = [fname, mname, lname, listname]
		except AttributeError:
			data = self._getnamealt()
		return data

	def _getnamealt(self):
		"""Alternative for _getname"""
		try:
			name = self.soup.find('span', class_='player-header--vitals-name').text
			sep = findall(r"[\w']+(?: Jr.)?", name)
			fname = sep[0]
			lname = sep[-1]
			mname = ''
			if len(sep) > 2:
				mname = sep[1]
				lname = ' '.join(sep[2:])
			data = [fname, mname, lname, name]
		except AttributeError:
			data = None
			raise PageNotLoaded(self.data['playerid'], self.data['gameid'])
		return data

	def _getdeets(self):
		try:
			row = self.soup.find('div', class_='player-header--vitals')('li')
			pos = row[0].text
			pos = sub('.?F', 'OF', pos)
			pos = sub('.?P', 'P', pos)
			[bats, throws] = row[1].text[-3:].split('/')
			dob = self.soup.find('div', class_='player-bio').ul
			dob = findall('[0-9]+/[0-9]+/[0-9]+', dob.text)[0].split('/')
			dob = '-'.join([dob[2], dob[0], dob[1]])
			data = [pos, dob, bats, throws]
		except AttributeError:
			data = self._getdeetsalt()
		return data

	def _getdeetsalt(self):
		"""Alternative for _getdeets"""
		row = self.soup.find('div', class_='player-header--vitals')('li')
		pos = row[0].text
		pos = sub('.?F', 'OF', pos)
		pos = sub('.?P', 'P', pos)
		[bats, throws] = row[1].text.split(': ')[-1].split('/')
		dob = None
		data = [pos, dob, bats, throws]
		return data

if __name__ == '__main__':
	args = [457759, 571771]
	RequestManager(Player, args).start()
	