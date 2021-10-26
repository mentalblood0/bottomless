import pytest

from tests import config
from bottomless import RedisInterface



def test_string():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface['key'] = '1'
	assert interface['key']() == '1'


def test_int():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface['key'] = 1
	assert interface['key']() == 1


def test_float():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface['key'] = 1.0
	assert interface['key']() == 1.0