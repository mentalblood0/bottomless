import pytest
from redis import Redis

from tests import config
from CRL import RedisInterface



db = Redis.from_url(config['db']['url'])


def test_nonexistent_key():

	interface = RedisInterface(db)
	interface.clear()

	assert interface['key'] == None
	assert interface['key']() == None


def test_deep():

	interface = RedisInterface(db)
	interface.clear()

	interface['1'] = 'one'
	interface['2'] = 'two'
	interface['1']['1']['1'] = 'one.one.one'
	interface['1']['2'] = 'one.two'

	assert interface() == {
		'1': {
			'1': {
				'1': 'one.one.one'
			},
			'2': 'one.two'
		},
		'2': 'two'
	}