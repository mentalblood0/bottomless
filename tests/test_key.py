from redis import Redis

from tests import config
from CRL import RedisInterface



def test_empty_path():
	
	interface = RedisInterface(config['db']['url'])

	assert interface.key == ''


def test_one_element_path():

	interface = RedisInterface(config['db']['url'])['one']

	assert interface.key == 'one'


def test_several_elements_path():

	interface = RedisInterface(config['db']['url'])['one']['two']['three']

	assert interface.key == 'one.two.three'