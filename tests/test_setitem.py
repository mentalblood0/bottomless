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

	interface_1 = RedisInterface(config['db']['url'])
	interface_2 = RedisInterface(config['db']['url'])
	interface_1.clear()

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
		args=[interface_1, key, seconds]
	)

	setter_dict = Thread(
		target=repeat_set_dict,
		args=[interface_2, key, seconds]
	)

	setter_bool.start()
	setter_dict.start()

	assert interface_1[key] == False or interface_1[key] == {
		'a': 1,
		'b': 2
	}