import time
from typing import overload
import uuid
from redis import Redis
from datetime import datetime

from tests import config
from CRL import RedisInterface



db = Redis.from_url(config['db']['url'])


def test_simple():

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


def test_realistic():

	interface = RedisInterface(db)
	interface.clear()

	n = 20 * 5
	start = time.time()

	for i in range(n):

		while True:
			id = uuid.uuid4().hex
			if not id in interface['sessions']:
				break
		
		interface['sessions'][id] = {
			'id': id,
			'name': i,
			'opened': 1,
			'datetime': str(datetime.now()), 
			'state': 'new',
			'commandCount': 0
		}
	
	end = time.time()

	overall = end - start

	assert overall < 1 