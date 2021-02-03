"""Selenium chrome browser class"""
from multiprocessing import Lock
from selenium import webdriver

class Browser(webdriver.Chrome):
	"""Selenium chrome browser class with a lock"""
	def __init__(self, driver_path: str, windows: int = 2, test: bool = False):
		opts = webdriver.ChromeOptions()
		if not test:
			opts.add_argument('--headless')
			opts.add_argument('--log-level=3')
			opts.add_argument('--ignore-certificate-errors')
			opts.add_argument('--ignore-certificate-errors-spki-list')
			opts.add_argument('--ignore-ssl-errors')
		webdriver.Chrome.__init__(self, driver_path, options=opts)
		self.lock = Lock()
		self.windows = [Window(self, 0)]
		for i in range(1, windows):
			self.execute_script('window.open('');')
			self.windows.append(Window(self, i))

	def acquire(self, block: bool = True):
		"""Acquire Lock"""
		return self.lock.acquire(block)

	def release(self):
		"""Release Lock"""
		return self.lock.release()

class Window():
	"""A browser's window"""
	def __init__(self, browser: Browser, num: int):
		self.browser = browser
		self.num = num
		self.lock = Lock()

	def get(self, url: str):
		"""Switches windows and gets url"""
		self.browser.acquire()
		self.browser.switch_to.window(self.browser.window_handles[self.num])
		self.browser.get(url)
		self.browser.release()

	@property
	def page_source(self):
		"""Returns page source"""
		self.browser.acquire()
		self.browser.switch_to.window(self.browser.window_handles[self.num])
		soup = self.browser.page_source
		self.browser.release()
		return soup

	@property
	def current_url(self):
		"""Returns current url"""
		self.browser.acquire()
		self.browser.switch_to.window(self.browser.window_handles[self.num])
		url = self.browser.current_url
		self.browser.release()
		return url

	def acquire(self, block: bool = True):
		"""Acquire Lock"""
		return self.lock.acquire(block)

	def release(self):
		"""Release Lock"""
		return self.lock.release()

	@property
	def is_locked(self) -> bool:
		"""Return whether Lock is in use"""
		if self.acquire(False):
			self.release()
			return False
		return True
