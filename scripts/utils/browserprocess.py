"""Manages and distributes work to multiple processes."""
from sys import modules
from os import getpid
from abc import ABC, abstractmethod
from multiprocessing import Process
from time import sleep
from bs4 import BeautifulSoup as bs
from browser import Window

class BrowserProcess(ABC, Process):
	"""For use with Browser_Manager.
	Creates thread and gets html from url.

	Abstract properties:
		url: string
		  	target url to scrape
		delay: int
			time (seconds) to wait for javascript-rendered html to load

	Abstract Methods:
		scrape(self): None
			method for scraping data from self.soup and inserting it into database
	"""
	def __init__(self, arg: list, window: Window):
		# pylint: disable=invalid-name
		"""Initializes self.
		*arg* argument(s) to be inserted in url string.
		*window* window object.
		"""
		window.acquire()
		ABC.__init__(self)
		Process.__init__(self)
		self.arg = arg
		self.window = window
		self.url = self.url.format(*self.arg)
		self.soup = None
		self.data = dict()

	def run(self):
		try:
			self.window.get(self.url)
			sleep(self.delay)
			self.soup = bs(self.window.page_source, 'html.parser')
			self.scrape()
			self.post()
			self.next()
		finally:
			self.window.release()

	@property
	def name(self) -> str:
		"""Unique name used for creating logs"""
		return __file__[:-3]

	@property
	def status(self) -> str:
		#pylint: disable=protected-access
		"""Return current status of process"""
		if self is modules['multiprocessing'].process._current_process:
			status = 'started'
		elif self._closed:
			status = 'closed'
		elif self._parent_pid != getpid():
			status = 'unknown'
		elif self._popen is None:
			status = 'initial'
		else:
			if self._popen.poll() is not None:
				status = self.exitcode
			else:
				status = 'started'

		if isinstance(status, int):
			if status == 0:
				status = 'stopped'
			else:
				status = 'stopped[%s]' % modules['multiprocessing']\
						.process._exitcode_to_name.get(status, status)
		return status

	@property
	@abstractmethod
	def url(self) -> str:
		"""The target url string to scrape.

		Should be in the form of "domain.com/{}/folder/{}" where any {} will be
		replaced using the str.format() method.
		"""

	@property
	@abstractmethod
	def delay(self) -> int:
		"""The time (seconds: int) to wait for javascript-rendered html to load"""

	@abstractmethod
	def scrape(self) -> None:
		"""Method for scraping data from self.soup and inserting it into database"""

	@abstractmethod
	def post(self) -> None:
		"""Method to post scraped data into database"""

	@abstractmethod
	def next(self) -> None:
		"""Method follow up"""
