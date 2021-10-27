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
	assert type(interface['key']()) == int
	assert interface['key'] == 1


def test_float():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface['key'] = 1.0
	assert type(interface['key']()) == float
	assert interface['key'] == 1.0


def test_bool():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface['key'] = True
	assert type(interface['key']()) == bool
	assert interface['key'] == True

	interface['key'] = False
	assert type(interface['key']()) == bool
	assert interface['key'] == False