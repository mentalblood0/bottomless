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
		self._prefixes_types['b'] = lambda b: b == 'True'

		self.pathToKey = pathToKey
		self.keyToPath = keyToPath

		self.__getByPattern = self.db.register_script("""
local keys = (redis.call('keys', ARGV[1]))
local values={}

for i,key in ipairs(keys) do 
	local val = redis.call('GET', key)
	values[i]=val
	i=i+1
end

local result = {}
result[1] = keys
result[2] = values

return result
""")

		self.__set = self.db.register_script("""
local keys = (redis.call('keys', ARGV[1]))
local values={}

for i,key in ipairs(keys) do 
	redis.call('DEL', key)
	i=i+1
end

local command = false
local N = false
local n = 1
local args = {}

for i,key in ipairs(ARGV) do
	if i ~= 1 then
		if command then
			if N == false then
				N = tonumber(key)+1
			else
				if n ~= N then
					args[n] = key
					n = n+1
				else
					redis.call(command, unpack(args))
					command = key
					N = false
					n = 1
					args = {}
				end
			end
		else
			command = key
		end
	end
end

redis.call(command, unpack(args))
""")

	def _getByPattern(self, pattern):
		return self.__getByPattern(args=[pattern])
	
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
		
		result = f'{self._types_prefixes[t]}{value}'

		return result

	def _parseType(self, s):

		s = self._default_type(s.decode())

		p = s[0]
		if not p in self._prefixes_types:
			return s

		t = self._prefixes_types[p]
		return t(s[1:])
	
	@property
	def _subkeys_pattern(self):
		if self.key:
			return f'{self.key}.*'
		else:
			return '*'

	def _absolute_keys(self):
		return self.db.keys(self._subkeys_pattern)
	
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
			keyToPath=self.keyToPath
		)
		item._key = item_key
		item._path = item_path

		return item
	
	def __getitem__(self, key):
		return self._getitem([key])
	
	def _set(self, keys_to_delete_pattern, extra_keys_to_delete, pairs_to_set):

		args = [
			keys_to_delete_pattern, 
			*(['DEL', len(extra_keys_to_delete), *extra_keys_to_delete] if extra_keys_to_delete else []), 
			*(['MSET', len(pairs_to_set) * 2, *[e[i] for e in pairs_to_set.items() for i in (0, 1,)]] if pairs_to_set else [])
		]

		return self.__set(args=args)

	def set(self, value):

		pairs_to_set = {}
		keys_to_delete = []

		keys_to_delete_pattern = ''
		
		if (type(value) == dict) or (type(value) == list):
			pairs_to_set = {
				self.pathToKey(self.path + [str(p) for p in path]): v
				for path, v in flatten(value, enumerate_types=(list,)).items()
			}
		
		else:
			keys_to_delete_pattern = self._subkeys_pattern
			pairs_to_set[self.key] = value
		
		# (self.path == ['a', 'b', 'c']) => (delete keys ['a', 'a.b', 'a.b.c'])
		parent_keys = {
			self.pathToKey(self.keyToPath(key)[:i+1])
			for key in pairs_to_set
			for i in range(len(self.keyToPath(key)))
		}
		keys_to_delete += parent_keys

		for k, v in pairs_to_set.items():
			pairs_to_set[k] = self._dumpType(v)
		
		self._set(keys_to_delete_pattern, list(parent_keys), pairs_to_set)

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
		subkeys, values = self._getByPattern(self._subkeys_pattern)
		
		if not subkeys:
			return None

		for i in range(len(subkeys)):

			k = subkeys[i]
			v = self._parseType(values[i])
			
			path = self.keyToPath(k.decode())[len(self.path):]
			
			r = result
			for p in path[:-1]:
				if not p in r or (not type(r[p]) == dict):
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