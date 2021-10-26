from sharpener import Benchmark

from tests import config
from bottomless import RedisInterface



class simple(Benchmark):

	def prepare(self, keys_number):

		self.interface = RedisInterface(config['db']['url'])
		self.interface.clear()
		
		self.interface |= {
			i+1: i+1
			for i in range(keys_number)
		}
	
	def run(self, **kwargs):
		self.interface.keys()
	
	def clean(self, **kwargs):
		self.interface.clear()