from typing import Type
from redis import Redis
from flatten_dict import flatten
from redis.client import Pipeline

from . import RedisInterfaceIterator, Connection



class RedisInterface:

	def __init__(
		self, 
		db, 
		pipeline=None,
		pathToKey=lambda path: '.'.join(path),
		keyToPath=lambda key: key.split('.'),
		types_prefixes={
			str: 's',
			int: 'i',
			float: 'f',
			bool: 'b'
		},
		default_type=str
	):
		
		self._db = db if isinstance(db, Redis) else Redis.from_url(db)
		self._connection = Connection(self.db.connection_pool.connection_kwargs)
		self._pipeline = pipeline
		self._key = ''
		self._path = []
		self._types_prefixes = types_prefixes
		self._default_type = default_type

		self._prefixes_types = {
			value: key
			for key, value in types_prefixes.items()
		}

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
	
	@property
	def connection(self):
		return self._connection
	
	@property
	def types_prefixes(self):
		return self._types_prefixes
	
	@property
	def default_type(self):
		return self._default_type

	def pipe(self, pipeline=None):
		
		if self._pipeline:
			self.execute()
		
		self._pipeline = pipeline or self.db.pipeline()
	
	def execute(self):
		pipeline = self._pipeline
		self._pipeline = None
		pipeline.execute()
	
	def clone(self):
		return RedisInterface(
			db=self.db,
			pathToKey=self.pathToKey,
			keyToPath=self.keyToPath,
			types_prefixes=self.types_prefixes,
			default_type=self.default_type
		)
	
	def _dumpType(self, value):

		t = type(value)
		t = t if t in self._types_prefixes else self._default_type
		
		return f'{self._types_prefixes[t]}{value}'
	
	def _parseType(self, s):

		s = self._default_type(s.decode())

		p = s[0]
		if not p in self._prefixes_types:
			return s

		t = self._prefixes_types[p]
		return t(s[1:])

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

		for k in [self.key] + self._absolute_keys():
			self.db.pexpire(k, int(seconds * 1000))
	
	def _getitem(self, subpath):

		item_path = self.path + [str(p) for p in subpath]

		item_key = self.pathToKey(item_path)
		valid_item_path = self.keyToPath(item_key)
		
		if item_path != valid_item_path:
			raise IndexError(f'Invalid path: {item_path}, maybe you mean {valid_item_path} ?')

		item = RedisInterface(
			db=self.db,
			pathToKey=self.pathToKey,
			keyToPath=self.keyToPath,
			types_prefixes=self.types_prefixes,
			default_type=self.default_type
		)
		item._key = item_key
		item._path = item_path

		return item
	
	def __getitem__(self, key):
		return self._getitem([key])

	def set(self, value):

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
		parent_keys = {
			self.pathToKey(self.keyToPath(key)[:i+1]).encode() # because there byte strings in keys
			for key in pairs_to_set
			for i in range(len(self.keyToPath(key)))
		}
		keys_to_delete += parent_keys

		pipeline = self.db.pipeline()
		
		if keys_to_delete:
			pipeline.delete(*keys_to_delete)
		
		for k, v in pairs_to_set.items():
			pairs_to_set[k] = self._dumpType(v)
		
		pipeline.mset(pairs_to_set)

		pipeline.execute()

		# if self._pipeline:
		# 	pipeline.execute()

	def __setitem__(self, key, value):

		if type(key) == int:
			key = str(key)

		if isinstance(value, RedisInterface):
			value = value()

		self[key].set(value)
	
	def clear(self):

		keys_to_delete = [self.key] + self._absolute_keys()
		if keys_to_delete:
			self.db.delete(*keys_to_delete)

	def __delitem__(self, key):
		self[key].clear()
	
	def __eq__(self, other):

		if isinstance(other, RedisInterface):
			if self.connection == other.connection:
				return self.key == other.key
			return self() == other()
		else:
			return self() == other
	
	def __call__(self):

		self_value = self.db.get(self.key)

		if self_value != None:
			return self._parseType(self_value)
		
		result = {}
		subkeys = self._absolute_keys()
		
		if not subkeys:
			return None
		
		values = self.db.mget(subkeys)

		for i in range(len(subkeys)):

			k = subkeys[i]
			v = self._parseType(values[i])
			
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
		self.set(other)
	
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
	
	def __add__(self, other):
		
		if not self.connection == other.connection:
			raise TypeError(f'Can not add: connections are not equal: {self.connection}, {other.connection}')

		return self._getitem(other.path)



import sys
sys.modules[__name__] = RedisInterface