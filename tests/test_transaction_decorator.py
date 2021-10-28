import uuid
import pytest
from loguru import logger
from functools import partial
from redis.client import Pipeline

from tests import config
from bottomless import RedisInterface



class ClientDbMock:
	def __init__(self, db):
		self.db = db


def getTransaction(flag, flag_value, f, args, kwargs):
	
	args = list(args) # default is tuple which not support item assignment
	
	def transaction_f(pipe):

		self = args[0]
		piped_self = ClientDbMock(
			RedisInterface(self.db.db, pipe)
		)
		args[0] = piped_self

		if flag != flag_value:
			flag.set(flag_value)
		
		pipe.multi()
		
		return f(*args, **kwargs)
	
	return transaction_f


def transaction(getInterface):

	def decorator(f):
		
		def new_f(*args, **kwargs):

			self = args[0]
			flag = self.db['locks'] + getInterface(*args, **kwargs)
			flag_value = uuid.uuid4().hex
			flag.set(flag_value)
			
			transaction_f = getTransaction(flag, flag_value, f, args, kwargs)

			result = self.db.db.transaction(transaction_f, flag.key, value_from_callable=True)
			return result

		return new_f
	
	return decorator


class ClientDb:

	def __init__(self, url):
		self.db = RedisInterface(url)
	
	@transaction(lambda self, id: self.db['sessions'][id]['state'])
	def getSessionState(self, id):
		return self.db['sessions'][id]['state']()


def test_basic():

	db = ClientDb(config['db']['url'])

	db.db.clear()
	id = 'some_id'
	state = 'new'

	db.db['sessions'][id]['state'] = 'new'

	assert db.getSessionState(id) == state