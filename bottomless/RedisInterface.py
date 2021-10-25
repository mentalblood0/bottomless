from redis import Redis
from flatten_dict import flatten

from . import RedisInterfaceIterator



class RedisInterface:

	def __init__(
		self, 
		db, 
		pathToKey=lambda path: '.'.join(path),
		keyToPath=lambda key: key.split('.')
	):
		
		self._db = db if isinstance(db, Redis) else Redis.from_url(db)
		self._key = ''
		self._path = []

		self.pathToKey = pathToKey
		self.keyToPath = keyToPath
	
	@property
	def db(self):
		return self._db
	
	@property
	def path(self):
		return self._path
	
	@property
	def key(self):
		return self._key
	
	def _absolute_keys(self):
		if self.key:
			return self.db.keys(f'{self.key}.*')
		else:
			return self.db.keys()
	
	def keys(self):
		return {
			self.keyToPath(k.decode())[len(self.path)] 
			for k in self._absolute_keys()
		}
	
	def expire(self, seconds):
		self.db.expire(self.key, seconds)
	
	def __getitem__(self, key):

		if type(key) == int:
			key = str(key)

		item_path = self.path + [key]

		item_key = self.pathToKey(item_path)
		valid_item_path = self.keyToPath(item_key)
		
		if item_path != valid_item_path:
			raise IndexError(f'Invalid path: {item_path}, maybe you mean {valid_item_path} ?')

		item = RedisInterface(
			db=self.db,
			pathToKey=self.pathToKey,
			keyToPath=self.keyToPath
		)
		item._key = item_key
		item._path = item_path

		return item

	def _set(self, value):

		pairs_to_set = {}
		keys_to_delete = []
		
		if (type(value) == dict) or (type(value) == list):
			pairs_to_set = {
				self.pathToKey(self.path + [str(p) for p in path]): v
				for path, v in flatten(value, enumerate_types=(list,)).items()
			}
		
		else:
			keys_to_delete += self._absolute_keys()
			pairs_to_set[self.key] = value
		
		# (self.path == ['a', 'b', 'c']) => (delete keys ['a', 'a.b', 'a.b.c'])
		keys_to_delete += [
			self.pathToKey(self.path[:i+1]).encode() # because there byte strings in keys
			for i in range(len(self.path))
		]
		if keys_to_delete:
			self.db.delete(*keys_to_delete)
		
		self.db.mset(pairs_to_set)

	def __setitem__(self, key, value):

		if type(key) == int:
			key = str(key)

		if isinstance(value, RedisInterface):
			value = value()

		self[key]._set(value)
	
	def clear(self):

		keys_to_delete = [self.key] + self._absolute_keys()
		if keys_to_delete:
			self.db.delete(*keys_to_delete)

	def __delitem__(self, key):
		self[key].clear()
	
	def __eq__(self, other):

		self_value = self()
		if isinstance(other, RedisInterface):
			other_value = other()
		else:
			other_value = other

		return self_value == other_value
	
	def __call__(self):

		self_value = self.db.get(self.key)

		if self_value != None:

			if type(self_value) == bytes:
				self_value = self_value.decode()
			
			if type(self_value) == str:
				try:
					self_value = int(self_value)
				except ValueError:
					try:
						self_value = float(self_value)
					except ValueError:
						pass
			
			return self_value
		
		result = {}
		subkeys = self._absolute_keys()
		
		if not subkeys:
			return None
		
		values = self.db.mget(subkeys)

		for i in range(len(subkeys)):

			k = subkeys[i]
			v = values[i].decode()
			try:
				v = int(v)
			except ValueError:
				try:
					v = float(v)
				except ValueError:
					pass
			
			path = self.keyToPath(k.decode())[len(self.path):]
			
			r = result
			for p in path[:-1]:
				if not p in r:
					r[p] = {}
				r = r[p]
			
			r[path[-1]] = v
		
		return result
	
	def __contains__(self, item):

		key = self[item].key

		if self.db.get(key) != None:
			return True
		else:
			return bool(self.db.keys(f'{key}.*'))
	
	def update(self, other: dict):
		self._set(other)
	
	def __ior__(self, other: dict): # |=
		self.update(other)
		return self
	
	def __len__(self):
		return len(self.keys())
	
	def append(self, value):
		self[len(self)] = value
	
	def __iadd__(self, other: list): # +=

		initial_length = len(self)

		self.update({
			initial_length + i: other[i]
			for i in range(len(other))
		})

		return self
	
	def __iter__(self):
		return RedisInterfaceIterator(self)



import sys
sys.modules[__name__] = RedisInterface