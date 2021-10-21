from redis import Redis

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
	
	def keys(self):

		if self.key:
			absolute_keys = self.db.keys(f'{self.key}.*')
		else:
			absolute_keys = self.db.keys()

		absolute_paths = [self.keyToPath(k.decode()) for k in absolute_keys]

		return {
			p[len(self.path)]
			for p in absolute_paths
		}
	
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

	def _set(self, value, pipeline=None):

		db = pipeline or self.db
		if not pipeline:
			self.clear(db)

		if type(value) == dict:
			for k, v in value.items():
				if isinstance(v, RedisInterface):
					v = v()
				self.__setitem__(k, v, pipeline)
		
		elif type(value) == list:
			for i in range(len(value)):
				v = value[i]
				if isinstance(v, RedisInterface):
					v = v()
				self.__setitem__(i, v, pipeline)
		
		else:
			db.set(self.key, value)

	def __setitem__(self, key, value, pipeline=None):

		if type(key) == int:
			key = str(key)

		if isinstance(value, RedisInterface):
			value = value()
		
		db = pipeline or self.db.pipeline()
		if not pipeline:
			self[key].clear(db)

		# (self.path == ['a', 'b', 'c']) => (delete keys ['a', 'a.b', 'a.b.c'])
		for i in range(len(self.path)):
			key_to_delete = self.pathToKey(self.path[:i+1]).encode() # because there byte strings in keys
			db.delete(key_to_delete)

		self[key]._set(value, db)

		if not pipeline:
			db.execute()
	
	def clear(self, pipeline=None):

		db = pipeline or self.db

		if self.key:
			keys_to_delete = [self.key] + self.db.keys(f'{self.key}.*')
		else:
			keys_to_delete = self.db.keys()

		if keys_to_delete:
			db.delete(*keys_to_delete)

	def __delitem__(self, key):
		self[key].clear()
	
	def _get(self):

		value = self.db.get(self.key)

		if type(value) == bytes:
			value = value.decode()
		
		if type(value) == str:
			try:
				value = int(value)
			except ValueError:
				try:
					value = float(value)
				except ValueError:
					pass

		return value
	
	def __eq__(self, other):

		self_value = self()
		if isinstance(other, RedisInterface):
			other_value = other()
		else:
			other_value = other

		return self_value == other_value
	
	def __call__(self):

		self_value = self._get()
		if self_value != None:
			return self_value
		
		result = {}
		if len(self.key):
			subkeys = self.db.keys(f'{self.key}.*')
		else:
			subkeys = self.db.keys()
		
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

		pipeline = self.db.pipeline()
		self._set(other, pipeline)
		pipeline.execute()
	
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