import pytest

from tests import config
from bottomless import RedisInterface



def test_basic():

	interface = RedisInterface(config['db']['url'])
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


def test_valid_key():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	sessions = [{
		f'session {i}': {
			'name': i,
			'data': 'lalala'
		}
	} for i in range(5)]

	interface['sessions'] = sessions

	assert len(interface['sessions'].keys()) == 5
	assert list(interface['sessions']) == sessions


def test_invalid_key():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	assert list(interface['sessions']) == []