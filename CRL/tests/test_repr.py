import pytest
from redis import Redis

from tests import config
from CRL import RedisInterface



db = Redis.from_url(config['db']['url'])


def test_valid_key():

	interface = RedisInterface(db)

	db.set('key', 'value')

	assert interface['key'] == 'value'


def test_invalid_key():

	interface = RedisInterface(db)

	db.delete('key')

	with pytest.raises(KeyError):
		interface['key'] == 'value'