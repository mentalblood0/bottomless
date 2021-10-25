import pytest
from time import sleep

from tests import config
from bottomless import RedisInterface



def test_basic():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface['key'] = 'value'
	interface['key'].expire(0.1)

	sleep(0.1)

	assert interface['key']() == None


def test_complex():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface['key'] = {
		'a': 1,
		'b': {
			'c': 3
		}
	}
	interface['key'].expire(0.1)

	sleep(0.1)

	assert interface['key']() == None