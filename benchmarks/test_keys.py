import time
from redis import Redis

from tests import config
from CRL import RedisInterface



db = Redis.from_url(config['db']['url'])


def test_keys():

	interface = RedisInterface(db)
	interface.clear()
	
	
	keys_number = 10 ** 3
	interface |= {
		i+1: i+1
		for i in range(keys_number)
	}

	n = 4 * 10 ** 2
	start = time.time()
	for i in range(n):
		interface.keys()
	end = time.time()

	overall = end - start

	assert overall < 1