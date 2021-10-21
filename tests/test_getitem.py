import pytest
from redis import Redis

from tests import config
from CRL import RedisInterface



db = Redis.from_url(config['db']['url'])


def test_empty_key():

	interface = RedisInterface(db)

	with pytest.raises(IndexError):
		interface['']


def test_valid_key():

	interface = RedisInterface(db)
	one = interface['one']

	assert one.key == 'one'


def test_multi_key():

	interface = RedisInterface(db, ['one', 'two', 'three'])

	with pytest.raises(IndexError):
		interface['one.two']