import json

from CRL.RedisInterfaceIterator import RedisInterfaceIterator



class RedisInterface:

	def __init__(
		self, 
		db, 
		path=[], 
		check_path=lambda path: not any([(not p) or ('.' in p) for p in path]), 
		compose_key=lambda p: '.'.join(p), 
		serialize=json.dumps, 
		deserialize=json.loads
	):
		
		self._db = db
		self._path = path

		self.serialize = serialize
		self.deserialize = deserialize
		self.check_path = check_path
		self.compose_key = compose_key

		self._length = 0

		assert self.check_path(self.path)
		self._key = self.compose_key(self.path)
	
	@property
	def db(self):
		return self._db
	
	@property
	def path(self):
		return self._path
	
	@property
	def key(self):
		return self._key
	
	def keys(self):

		pattern = f'{self.key}.*' if self.key else '*'

		absolute_keys = self.db.scan(match=pattern)[1]
		absolute_paths = [k.decode().split('.') for k in absolute_keys]

		return [
			p[len(self.path)]
			for p in absolute_paths
		]
	
	def __getitem__(self, key):

		if type(key) == int:
			key = str(key)

		return RedisInterface(
			self.db, 
			self.path + [key],
			self.check_path,
			self.compose_key,
			self.serialize,
			self.deserialize
		)

	def _set(self, value):

		self.db.delete(self.key)

		if type(value) == dict:
			for k, v in value.items():
				self[k] = v
		elif type(value) == list:
			for i in range(len(value)):
				self[i] = value[i]
		else:
			self.db.set(self.key, value)

	def __setitem__(self, key, value):

		if type(key) == int:
			
			if key < 0 or key >= self._length:
				raise IndexError('list assignment index out of range')
		
			key = str(key)

		if len(self.path):
			keys = {
				k: True
				for k in 
				self.db.scan(match=f"{self.path[0]}")[1] + 
				self.db.scan(match=f"{self.path[0]}.*")[1]
			}

		# (self.path == ['a', 'b', 'c']) => (delete keys ['a', 'a.b', 'a.b.c'])
		for i in range(len(self.path)):
			key_to_delete = self.compose_key(self.path[:i+1]).encode() # because there byte strings in keys
			if key_to_delete in keys:
				self.db.delete(key_to_delete)

		self[key]._set(value)
	
	def clear(self):

		pattern = f'{self.key}.*' if self.key else '*'

		keys_to_delete = [self.key] + self.db.scan(match=pattern)[1]

		if keys_to_delete:
			if not self.db.delete(*keys_to_delete):
				pass
				# raise KeyError(f"No keys starting with '{self.key}'")

	def __delitem__(self, key):
		self[key].clear()
	
	def _get(self):

		value = self.db.get(self.key)

		try:
			result = self.deserialize(value)
		except Exception:
			result = value.decode() if type(value) == bytes else value
		
		return result
	
	def __eq__(self, other):

		self_value = self._get()
		other_value = other._get() if hasattr(other, '_get') else other

		return self_value == other_value
	
	def __call__(self):

		self_value = self._get()
		if self_value != None:
			return self_value

		return {
			k: self[k]()
			for k in self.keys()
		}
	
	def __contains__(self, item):
		return item in self.keys()
	
	def update(self, other: dict):
		self._set(other)
	
	def __ior__(self, other: dict): # |=
		self.update(other)
		return self
	
	def __len__(self):	
		return self._length
	
	def append(self, other: list):

		self._length += len(other)
		
		for i in range(len(other)):
			self[i] = other[i]
	
	def __iadd__(self, other: list): # +=
		self.append(other)
		return self
	
	def __iter__(self):
		return RedisInterfaceIterator(self)



import sys
sys.modules[__name__] = RedisInterface