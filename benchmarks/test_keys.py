import time
import cProfile

from tests import config
from CRL import RedisInterface



def test_keys():

	interface = RedisInterface(config['db']['url'])
	interface.clear()
	
	
	keys_number = 10 ** 3
	interface |= {
		i+1: i+1
		for i in range(keys_number)
	}

	n = 1 * 10 ** 2
	start = time.time()
	cProfile.runctx("""
for i in range(n):
	interface.keys()""", locals=locals(), globals=globals())

	end = time.time()

	overall = end - start

	assert overall < 1