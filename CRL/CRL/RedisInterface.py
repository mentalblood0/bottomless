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
		self.db.delete(self.key)

	def __delitem__(self, key):
		self[key]._delete()
	
	def __repr__(self):
		return 



import sys
sys.modules[__name__] = RedisInterface