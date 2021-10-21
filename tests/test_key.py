from redis import Redis

from tests import config
from CRL import RedisInterface



db = Redis.from_url(config['db']['url'])


def test_empty_path():
	
	interface = RedisInterface(db)

	assert interface.key == ''


def test_one_element_path():

	interface = RedisInterface(db)['one']

	assert interface.key == 'one'


def test_several_elements_path():

	interface = RedisInterface(db)['one']['two']['three']

	assert interface.key == 'one.two.three'