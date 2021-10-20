from time import sleep

from . import RedisInterface



class Lock:

	locks_path = ['_RedisInterface_locks']

	def __init__(self, interface):
		self.lock_interface = RedisInterface(
			db=interface.db, 
			path=self.locks_path + interface.path
		)

	def acquire(self):
		self.lock_interface._set(1)
	
	def isAcquired(self):
		return self.lock_interface()
	
	def release(self):
		self.lock_interface._set(0)

	def __enter__(self):

		while self.isAcquired():
			sleep(0.1)
		self.acquire()
		
		return self
	
	def __exit__(self, exc_type, exc_value, traceback):
		self.release()



import sys
sys.modules[__name__] = Lock