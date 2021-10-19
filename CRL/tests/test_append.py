import pytest
from redis import Redis

from tests import config
from CRL import RedisInterface



db = Redis.from_url(config['db']['url'])


def test_invalid_index():

	interface = RedisInterface(db)
	interface.clear()

	with pytest.raises(IndexError):
		interface[1] = '1'
	
	with pytest.raises(IndexError):
		interface[0] = '0'


def test_append():

	interface = RedisInterface(db)
	interface.clear()

	interface['key'] = 'value'
	interface['another_key'] = 'another_value'

	l = 10
	m = [i for i in range(l)]
	interface += m

	print(interface, m)

	assert len(interface) == len(m)

	for i in range(len(m)):
		assert interface[i] == m[i]