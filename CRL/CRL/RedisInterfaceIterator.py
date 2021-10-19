class RedisInterfaceIterator:

	def __init__(self, interface):
		
		self.current = 0
		self.length = len(interface)
		self.interface = interface
	
	def __iter__(self):
		return self
	
	def __next__(self):

		if self.current == self.length:
			raise StopIteration()
		
		result = self.interface[self.current]
		self.current += 1

		return result