import time
import uuid
import cProfile
from datetime import datetime

from tests import config
from CRL import RedisInterface



def test_simple():

	interface = RedisInterface(config['db']['url'])
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

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	n = 10 ** 2
	start = time.time()

	cProfile.runctx("""
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
	}""", locals=locals(), globals = globals())
	
	end = time.time()

	overall = end - start

	assert overall < 1