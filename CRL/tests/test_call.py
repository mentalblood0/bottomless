import pytest
from redis import Redis

from tests import config
from CRL import RedisInterface



db = Redis.from_url(config['db']['url'])


def test_basic():

	interface = RedisInterface(db)

	interface._delete()

	interface['1'] = 'one'
	interface['2'] = 'two'
	interface['1']['1'] = 'one.one'
	interface['1']['2'] = 'one.two'

	assert interface() == {
		'1': {
			'self': 'one',
			'1': {
				'self': 'one.one'
			},
			'2': {
				'self': 'one.two'
			}
		},
		'2': {
			'self': 'two'
		}
	}