from redis import Redis
from flatten_dict import flatten

from . import Connection, scripts



class RedisInterface:

	def __init__(
		self, 
		db, 
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
		
		self.__db = db if isinstance(db, Redis) else Redis.from_url(db)
		self.__connection = Connection(self.db.connection_pool.connection_kwargs)
		self.__key = ''
		self.__path = []
		self.__types_prefixes = types_prefixes
		self.__default_type = default_type

		self.__prefixes_types = {
			value: key
			for key, value in types_prefixes.items()
		}
		self.__prefixes_types['b'] = lambda b: b == 'True'

		self.__pathToKey = pathToKey
		self.__keyToPath = keyToPath

		self.__scripts = {}
		script_caller_wrapper = lambda c: lambda *args: c(args=args)
		for name, script in scripts.items():
			script_caller = self.db.register_script(script)
			wrapped_script_caller = script_caller_wrapper(script_caller)
			self.__scripts[name] = wrapped_script_caller
	
	@property
	def db(self):
		return self.__db
	
	@property
	def path(self):
		return self.__path
	
	@property
	def key(self):
		return self.__key
	
	@property
	def connection(self):
		return self.__connection
	
	@property
	def types_prefixes(self):
		return self.__types_prefixes
	
	@property
	def prefixes_types(self):
		return self.__prefixes_types
	
	@property
	def default_type(self):
		return self.__default_type
	
	@property
	def pathToKey(self):
		return self.__pathToKey
	
	@property
	def keyToPath(self):
		return self.__keyToPath
	
	def __dumpType(self, value):

		t = type(value)
		t = t if t in self.__types_prefixes else self.__default_type
		
		result = f'{self.__types_prefixes[t]}{value}'

		return result

	def __parseType(self, s):

		s = self.__default_type(s.decode())

		p = s[0]
		if not p in self.__prefixes_types:
			return s

		t = self.__prefixes_types[p]
		return t(s[1:])
	
	@property
	def subkeys_pattern(self):
		if self.key:
			return f'{self.key}.*'
		else:
			return '*'

	def __absolute_keys(self):
		return self.db.keys(self.subkeys_pattern)
	
	def keys(self):
		return {
			self.keyToPath(k.decode())[len(self.path)] 
			for k in self.__absolute_keys()
		}
	
	def expire(self, seconds):
		self.__scripts['pexpireByPattern'](self.subkeys_pattern, int(seconds * 1000), self.key)
	
	def __getitem(self, subpath):

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
		item.__key = item_key
		item.__path = item_path

		return item
	
	def __getitem__(self, key):
		return self.__getitem([key])
	
	def composeSetArgs(self, keys_to_delete_patterns, extra_keys_to_delete, pairs_to_set):
		return [
			len(keys_to_delete_patterns),
			*keys_to_delete_patterns, 
			*(['DEL', len(extra_keys_to_delete), *extra_keys_to_delete] if extra_keys_to_delete else []), 
			*(['MSET', len(pairs_to_set) * 2, *[e[i] for e in pairs_to_set.items() for i in (0, 1,)]] if pairs_to_set else [])
		]

	def set(self, value, clear=True):
		
		pairs_to_set = {}
		keys_to_delete_patterns = set()
		extra_keys_to_delete = set()
		
		if (type(value) == dict) or (type(value) == list):
			
			pairs_to_set = {
				self.pathToKey(self.path + [str(p) for p in path]): v
				for path, v in flatten(value, enumerate_types=(list,)).items()
			}

			extra_keys_to_delete |= {self.key}

			if clear:
				keys_to_delete_patterns = [self.subkeys_pattern]
			else:
				for new_key in pairs_to_set:
					new_path = self.keyToPath(new_key)
					short_new_key = self.pathToKey(new_path[:len(self.path)+1])
					keys_to_delete_patterns |= {f'{short_new_key}.*'}
		
		else:
			keys_to_delete_patterns = [self.subkeys_pattern]
			pairs_to_set[self.key] = value
		
		# (self.path == ['a', 'b', 'c']) => (delete keys ['a', 'a.b', 'a.b.c'])
		extra_keys_to_delete |= {
			self.pathToKey(self.keyToPath(key)[:i+1])
			for key in pairs_to_set
			for i in range(len(self.keyToPath(key)))
		}

		for k, v in pairs_to_set.items():
			pairs_to_set[k] = self.__dumpType(v)
		
		self.__scripts['set'](*self.composeSetArgs(
			keys_to_delete_patterns, 
			list(extra_keys_to_delete), 
			pairs_to_set
		))

	def __setitem__(self, key, value):

		if type(key) == int:
			key = str(key)

		if isinstance(value, RedisInterface):
			value = value()

		self[key].set(value)
	
	def clear(self):
		if self.key == '':
			self.db.flushdb()
		else:
			self.__scripts['set'](*self.composeSetArgs(
				keys_to_delete_patterns=[self.subkeys_pattern], 
				extra_keys_to_delete=[self.key], 
				pairs_to_set={}
			))

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
			return self.__parseType(self_value)
		
		result = {}
		subkeys, values = self.__scripts['getByPattern'](self.subkeys_pattern)

		for i in range(len(subkeys)):

			k = subkeys[i]
			v = self.__parseType(values[i])
			
			path = self.keyToPath(k.decode())[len(self.path):]
			
			r = result
			for p in path[:-1]:
				if not p in r or (not type(r[p]) == dict):
					r[p] = {}
				r = r[p]
			
			r[path[-1]] = v
		
		return result or None
	
	def __contains__(self, key):
		return self.__scripts['exists'](self[key].key)
	
	def update(self, other: dict):
		self.set(other, clear=False)
	
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
		for k in sorted(self.keys()):
			yield self[k]
	
	def __add__(self, other):
		
		if not self.connection == other.connection:
			raise TypeError(f'Can not add: connections are not equal: {self.connection}, {other.connection}')

		return self.__getitem(other.path)



import sys
sys.modules[__name__] = RedisInterface