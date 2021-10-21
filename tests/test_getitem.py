import pytest

from tests import config
from CRL import RedisInterface



def test_empty_key():

	interface = RedisInterface(config['db']['url'])
	interface['']


def test_valid_key():

	interface = RedisInterface(config['db']['url'])
	one = interface['one']

	assert one.key == 'one'


def test_multi_key():

	interface = RedisInterface(config['db']['url'])['one']['two']['three']

	with pytest.raises(IndexError):
		interface['one.two']