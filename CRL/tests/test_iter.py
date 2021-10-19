import pytest
from redis import Redis

from tests import config
from CRL import RedisInterface



db = Redis.from_url(config['db']['url'])


def test_basic():

	interface = RedisInterface(db)
	interface.clear()

	l = [{
		'key': i
	} for i in range(1, 4+1)]

	interface += l

	assert sorted(interface.keys()) == ['0', '1', '2', '3']

	i = 0
	for e in interface:
		assert e == interface[i]()
		i += 1
	
	assert list(interface) == l