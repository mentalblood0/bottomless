import pytest
from redis import Redis

from tests import config
from CRL import RedisInterface



db = Redis.from_url(config['db']['url'])


def test_valid_key():

	interface = RedisInterface(db)

	db.set('key', 'value')

	del interface['key']


def test_cascade():

	interface = RedisInterface(db)

	interface['1'] = 'one'
	interface['2'] = 'two'
	interface['1']['1'] = 'one.one'
	interface['1']['2'] = 'one.two'
	interface['11'] = 'oneone'

	del interface['1']

	assert interface['1']() == None
	assert interface['1'] == None
	assert interface['1']['1'] == None
	assert interface['1']['2'] == None
	assert interface['11'] == 'oneone'

	del interface['2']

	assert interface['2'] == None