import time
from redis import Redis

from tests import config
from CRL import RedisInterface



db = Redis.from_url(config['db']['url'])


def test_basic():

	interface = RedisInterface(db)
	interface.clear()
	
	start = time.time()
	n = 10 ** 3
	interface |= {
		i+1: i+1
		for i in range(n)
	}
	end = time.time()

	overall = end - start

	assert overall < 1