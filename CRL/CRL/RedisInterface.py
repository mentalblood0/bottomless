import json



class RedisInterface:

	def __init__(
		self, 
		db, 
		path=[], 
		check_path=lambda path: not any([(not p) or ('.' in p) for p in path]), 
		compose_key='.'.join, 
		serialize=json.dumps, 
		deserialize=json.loads
	):
		
		self._db = db
		self._path = path

		self.serialize = serialize
		self.deserialize = deserialize
		self.check_path = check_path
		self.compose_key = compose_key

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
		return self.db.scan(match=f'{self.key}.*')
	
	def __getitem__(self, key):
		return RedisInterface(
			self.db, 
			self.path + [key],
			self.check_path,
			self.compose_key,
			self.serialize,
			self.deserialize
		)

	def _set(self, value):
		
		data = self.serialize(value)

		self.db.set(self.key, data)

	def __setitem__(self, key, value):
		self[key]._set(value)
	
	def _delete(self):

		keys_to_delete = [self.key] + self.db.scan(match=f"{self.key}.*")[1]

		if keys_to_delete:
			if not self.db.delete(*keys_to_delete):
				raise KeyError(f"No keys starting with '{self.key}'")

	def __delitem__(self, key):
		self[key]._delete()
	
	def _get(self):

		value = self.db.get(self.key)

		try:
			result = self.deserialize(value)
		except Exception:
			result = value.decode() if type(value) == bytes else value
		
		return result
	
	def __eq__(self, other):

		print('__eq__', self, other)

		self_value = self._get()
		other_value = other._get() if hasattr(other, '_get') else other

		print('values:', self_value, other_value)

		return self_value == other_value



import sys
sys.modules[__name__] = RedisInterface