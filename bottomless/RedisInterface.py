from redis import Redis
from flatten_dict import flatten

from . import Connection



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
		
		self.__db = db if isinstance(db, Redis) else Redis.from_url(db)
		self.__connection = Connection(self.db.connection_pool.connection_kwargs)
		self.__pipeline = pipeline
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

		self.__contains = self.db.register_script("""
local value = redis.call('GET', ARGV[1])
local subkeys = (redis.call('KEYS', ARGV[1] .. '.*'))

return value or subkeys[1]
""")

	def _getByPattern(self, pattern):
		return self.__getByPattern(args=[pattern])
	
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

	def pipe(self, pipeline=None):
		self.__pipeline = pipeline or self.db.pipeline()
	
	def execute(self):
		pipeline = self.__pipeline
		self.__pipeline = None
		pipeline.execute()
	
	def clone(self):
		return RedisInterface(
			db=self.db,
			pathToKey=self.pathToKey,
			keyToPath=self.keyToPath,
			types_prefixes=self.types_prefixes,
			default_type=self.default_type
		)
	
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

		for k in [self.key] + self.__absolute_keys():
			self.db.pexpire(k, int(seconds * 1000))
	
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
	
	def _set(self, keys_to_delete_pattern, extra_keys_to_delete, pairs_to_set):

		args = [
			keys_to_delete_pattern, 
			*(['DEL', len(extra_keys_to_delete), *extra_keys_to_delete] if extra_keys_to_delete else []), 
			*(['MSET', len(pairs_to_set) * 2, *[e[i] for e in pairs_to_set.items() for i in (0, 1,)]] if pairs_to_set else [])
		]

		return self.__set(args=args)

	def set(self, value, clear=True):

		pairs_to_set = {}
		keys_to_delete = []

		keys_to_delete_pattern = ''
		
		if (type(value) == dict) or (type(value) == list):
			
			if clear:
				keys_to_delete_pattern = self.subkeys_pattern
			
			pairs_to_set = {
				self.pathToKey(self.path + [str(p) for p in path]): v
				for path, v in flatten(value, enumerate_types=(list,)).items()
			}
		
		else:
			keys_to_delete_pattern = self.subkeys_pattern
			pairs_to_set[self.key] = value
		
		# (self.path == ['a', 'b', 'c']) => (delete keys ['a', 'a.b', 'a.b.c'])
		parent_keys = {
			self.pathToKey(self.keyToPath(key)[:i+1])
			for key in pairs_to_set
			for i in range(len(self.keyToPath(key)))
		}
		keys_to_delete += parent_keys

		for k, v in pairs_to_set.items():
			pairs_to_set[k] = self.__dumpType(v)
		
		self._set(keys_to_delete_pattern, list(parent_keys), pairs_to_set)

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
			self._set(self.subkeys_pattern, [self.key], {})

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
		subkeys, values = self._getByPattern(self.subkeys_pattern)

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
	
	def _contains(self, key):
		return self.__contains(args=[key])
	
	def __contains__(self, key):
		return self._contains(self[key].key)
	
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