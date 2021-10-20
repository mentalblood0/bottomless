from time import sleep

from . import RedisInterface



class RedisInterfaceLock:

	locks_path = ['_RedisInterface_locks']

	def __init__(self, interface):

		lock_key = interface.compose_key(self.locks_path + interface.path)
		self.set = lambda x: interface.db.set(lock_key, x)
		self.get = lambda: interface.db.get(lock_key)

	def acquire(self):
		self.set(1)
	
	def isAcquired(self):
		return self.get()
	
	def release(self):
		self.set(0)

	def __enter__(self):

		while self.isAcquired():
			sleep(0.1)
		self.acquire()
		
		return self
	
	def __exit__(self, exc_type, exc_value, traceback):
		self.release()



import sys
sys.modules[__name__] = RedisInterfaceLock