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


def getTransaction(flag, f):
	
	def transaction_f(pipe):
		pipe.multi()
		return f()
	
	return transaction_f


def lock(getInterface):

	def decorator(f):
		
		def new_f(*args, **kwargs):

			args = list(args) # default is tuple which not support item assignment

			self = args[0]
			flag = self.db['locks'] + getInterface(*args, **kwargs)
			flag.set(uuid.uuid4().hex)
			
			transaction_f = getTransaction(flag, partial(f, *args, **kwargs))

			result = self.db.db.transaction(transaction_f, flag.key, value_from_callable=True)
			logger.warning(f'TRANSACTION RESULT IS {result}')
			return result

		return new_f
	
	return decorator


class ClientDb:

	def __init__(self, url):
		self.db = RedisInterface(url)
	
	@lock(lambda self, id: self.db['sessions'][id]['state'])
	def getSessionState(self, id):
		return self.db['sessions'][id]['state']()


def test_basic():

	db = ClientDb(config['db']['url'])

	db.db.clear()
	id = 'some_id'
	state = 'new'

	db.db['sessions'][id]['state'] = 'new'

	assert db.getSessionState(id) == state