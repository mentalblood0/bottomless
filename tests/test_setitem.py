import uuid
import pytest
from datetime import datetime

from tests import config
from CRL import RedisInterface



def test_basic():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface[1] = 'one'
	interface['2'] = 'two'
	interface['1']['1'] = 'one.one'
	interface['1']['2'] = 'one.two'

	assert interface['1'] != 'one'
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