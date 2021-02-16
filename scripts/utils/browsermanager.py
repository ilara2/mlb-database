"""Manages and distributes work to multiple processes."""
from browser import Browser, Window
from math import ceil

class BrowserManager():
	"""For use with a javascript-rendered site.
	Helper class to contain and manage Browser_Thread() process.
	"""
	def __init__(self, t_class: object, args: list, max_process: int = 5, num_windows: int = 5, test: bool = False):
		""" Initialize self.
		*t_class* Process object that will run scrapping
		*args* arguments to pass into t_class's url string
		*max_processes* max number of processes running at once (number of browsers running)
		**
		"""
		self.args = args
		self.t_class = t_class
		self.max_process = max_process if max_process * num_windows < len(args) else ceil(len(args)/num_windows)
		self.num_windows = num_windows
		self.test = test
		self.browsers = []
		self.processes = []
		self.windows = []

	def _startbrowsers(self) -> None:
		"""Starts webdriver browsers"""
		for _ in range(self.max_process):
			browser = Browser('../chromedriver.exe', self.num_windows, self.test)
			self.browsers.append(browser)
			self.windows += browser.windows


	def _nextwindow(self) -> Window:
		"""Returns next available tab"""
		for proc in self.processes:
			if proc.status == 'stopped':
				self.processes.remove(proc)
				proc.close()
		while True:
			for window in self.windows:
				if not window.is_locked:
					return window

	def _start(self):
		"""Start maximum number of processes"""
		num_args = len(self.args)
		for i in range(num_args):
			window = self._nextwindow()
			print('\t{} of {}\r'.format(i+1, num_args))
			process = self.t_class(self.args[i], window)
			self.processes.append(process)
			process.start()

	def _cleanup(self):
		"""Closes processes and browsers"""
		for proc in self.processes:
			proc.join()
			proc.terminate()
		for browser in self.browsers:
			browser.quit()

	def run(self):
		"""Starts the Manager"""
		try:
			self._startbrowsers()
			self._start()
		except (KeyboardInterrupt, SystemError):
			print("\nI'm shutting it down!\n")
		finally:
			self._cleanup()
		