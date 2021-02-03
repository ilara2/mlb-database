"""Scrape static web pages"""
from abc import ABC, abstractmethod
from threading import Thread
from time import sleep
from bs4 import BeautifulSoup as bs
import requests as r

class RequestThread(ABC, Thread):
	"""For use with RequestManager.
	Creates thread and gets html from url.

	Abstract properties:
		url: string
		  	target url to scrape

	Abstract Methods:
		scrape(self): None
			method for scraping data from self.soup and inserting it into database
	"""
	def __init__(self, arg: ..., sema: type):
		# pylint: disable=invalid-name
		"""Initializes self.
		*arg* argument(s) to be inserted in url string.
		*sema* a threading.Semaphore.
		"""
		ABC.__init__(self)
		Thread.__init__(self)
		self.arg = arg
		self.sema = sema
		if isinstance(arg, list):
			self.url = self.url.format(*self.arg)
		else:
			self.url = self.url.format(self.arg)
		self.soup = None
		self.data = dict()

	def run(self):
		sleep(self.delay)
		self.soup = bs(r.get(self.url).content, 'html.parser')
		self.sema.release()
		self.scrape()

	@property
	def name(self):
		return __file__[:-3]

	@property
	@abstractmethod
	def url(self):
		"""The target url."""

	@property
	@abstractmethod
	def delay(self):
		"""The time in seconds to sleep before a request is sent."""

	@abstractmethod
	def scrape(self):
		"""The method use to scrape the url."""
