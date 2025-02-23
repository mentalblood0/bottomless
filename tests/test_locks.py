import pytest
from time import sleep
from redis import Redis
from threading import Thread

from tests import config
from bottomless import RedisInterface



def test_basic():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	results = {'long_get': None}

	def long_set(interface, key, value):
		interface[key] = value
	
	def long_get(interface, key, valid_key, results):
		sleep(1)
		print(len(interface), valid_key)
		results['long_get'] = (interface[key]() == valid_key)
	
	n = 4 * 10 ** 2
	key = 'key'
	value = {
		i+1: i+1
		for i in range(n)
	}
	
	setter = Thread(
		target=long_set,
		args=[interface, key, value]
	)

	getter = Thread(
		target=long_get,
		args=[interface[key], n, n, results]
	)

	setter.start()
	getter.start()

	setter.join()
	getter.join()

	assert results['long_get'] == True