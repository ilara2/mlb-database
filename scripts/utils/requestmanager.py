"""Manages RequestThreads"""
from threading import Semaphore

class RequestManager():
	"""Manages RequestThreads use for static web-pages"""
	def __init__(self, t_class, args, max_threads=10):
		self.args = args
		self.t_class = t_class
		self.max_threads = max_threads if max_threads < len(args) else len(args)
		self.sema = Semaphore(value=self.max_threads)

	def _startthreads(self):
		threads = []
		num_args = len(self.args)
		for i in range(num_args):
			self.sema.acquire()
			# print('\t{} of {}\r'.format(i+1, num_args))
			thread = self.t_class(self.args[i], self.sema)
			threads.append(thread)
			thread.start()
		for thread in threads:
			thread.join()

	def start(self):
		"""Starts the Thread Manager"""
		self._startthreads()
