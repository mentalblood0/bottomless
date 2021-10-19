import pytest
from redis import Redis

from tests import config
from CRL import RedisInterface



db = Redis.from_url(config['db']['url'])


def test_basic():

	interface = RedisInterface(db)
	interface.clear()

	interface += [1, 2, 3, 4]

	i = 0
	for e in interface:
		assert e == interface[i]
		i += 1
	
	assert list(interface) == [1, 2, 3, 4]