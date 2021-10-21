import time
import cProfile
from redis import Redis

from tests import config
from CRL import RedisInterface



db = Redis.from_url(config['db']['url'])


def test_simple():

	interface = RedisInterface(db)
	interface.clear()
	
	keys_number = 10 ** 3
	interface |= {
		i+1: i+1
		for i in range(keys_number)
	}

	n = 10
	start = time.time()
	for i in range(n):
		interface()
	end = time.time()

	overall = end - start

	assert overall < 1


def test_realistic():

	interface = RedisInterface(db)
	interface.clear()

	commands = interface['commands']

	commands += [{
		'id': str(i),
		'command': {
			'id': 'lalala',
			'name': 'connect',
			'type': 'cmdConnect',
			'protocol': 't0'
		},
		'answer': {
			'type': 'ansOk'
		},
		'answer_sent': 0
	} for i in range(1)]

	n = 1000
	start = time.time()

	cProfile.runctx("""
for i in range(n):

	result = []

	for c in commands:
		if not c['answer_sent']():
			answer = c['answer']()
			if answer != None:
				answer = answer | {'commandId': c['id']()}
				result.append(answer)""", locals=locals(), globals=globals())
	
	end = time.time()

	overall = end - start

	assert overall < 1