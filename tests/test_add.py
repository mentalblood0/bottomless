import pytest

from tests import config
from bottomless import RedisInterface



def test_simple():

	interface = RedisInterface(config['db']['url'])

	assert interface['a'] + interface['b'] == interface['a']['b']


def test_not_equal_connections():

	a = RedisInterface('redis://1.1.1.1:1111')
	b = RedisInterface('redis://2.2.2.2:2222')

	with pytest.raises(TypeError):
		a['a'] + b['b']


def test_complex():

	interface = RedisInterface(config['db']['url'])

	assert interface['a']['b'] \
		 + interface['c']['d']['e'] \
		 + interface['f']['g'] \
		 == interface['a']['b']['c']['d']['e']['f']['g']