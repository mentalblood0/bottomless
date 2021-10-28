import uuid
import time
import pytest
from datetime import datetime
from threading import Thread

from tests import config
from bottomless import RedisInterface



def test_basic():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface[1] = 'one'
	interface['2'] = 'two'
	interface['1']['1'] = 'one.one'
	interface['1']['2'] = 'one.two'

	assert interface['1'] != 'one'
	print(interface[2](), 'two')
	assert interface[2] == 'two'
	assert interface['1']['1'] == 'one.one'
	assert interface['1']['2'] == 'one.two'


def test_complex():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface['1'] = {
		'1': 'one.one',
		'2': 'one.two'
	}

	assert interface['1']['1'] == 'one.one'
	assert interface['1']['2'] == 'one.two'


def test_many_complex():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	sessions = {}

	for i in range(2):

		existing_sessions_ids = interface['sessions'].keys()

		while True:
			id = uuid.uuid4().hex
			if not id in existing_sessions_ids:
				break
		
		new_session = {
			'id': id,
			'name': 'name',
			'opened': 1,
			'datetime': str(datetime.now()), 
			'state': 'new',
			'commandCount': 0
		}
		sessions[id] = new_session
		interface['sessions'][id] = new_session
	
	assert interface['sessions'] == sessions


def test_async():

	interface = RedisInterface(config['db']['url'])
	interface_2 = RedisInterface(config['db']['url'])
	interface.clear()

	report = {}

	def repeat_set_bool(interface, key, seconds, report):
		start = time.time()
		while start + seconds > time.time():
			interface[key] = False
			report['bool'] = True
	
	def repeat_set_dict(interface, key, seconds, report):
		start = time.time()
		while start + seconds > time.time():
			interface[key] = {
				'a': 1,
				'b': 2
			}
			report['dict'] = True
	
	seconds = 2
	key = 'key'
	
	setter_bool = Thread(
		target=repeat_set_bool,
		args=[interface, key, seconds, report]
	)

	setter_dict = Thread(
		target=repeat_set_dict,
		args=[interface_2, key, seconds, report]
	)

	setter_bool.start()
	setter_dict.start()
	
	start = time.time()
	while start + seconds > time.time():
		keys, values = interface._getByPattern(interface._subkeys_pattern)
		assert keys == [b'key'] or sorted(keys) == [b'key.a', b'key.b']
		# result = interface()['key']
		# assert result == False or result == {
		# 	'a': 1,
		# 	'b': 2
		# }


def test_async_wait():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	def repeat_set_bool(interface, key, seconds):
		start = time.time()
		while start + seconds > time.time():
			interface[key] = False
	
	def repeat_set_dict(interface, key, seconds):
		start = time.time()
		while start + seconds > time.time():
			interface[key] = {
				'a': 1,
				'b': 2
			}
	
	seconds = 2
	key = 'key'
	
	setter_bool = Thread(
		target=repeat_set_bool,
		args=[interface, key, seconds]
	)

	setter_dict = Thread(
		target=repeat_set_dict,
		args=[interface, key, seconds]
	)

	setter_bool.start()
	setter_dict.start()

	setter_bool.join()
	setter_dict.join()

	result = interface[key]()

	assert interface[key]() == False or interface[key] == {
		'a': 1,
		'b': 2
	}