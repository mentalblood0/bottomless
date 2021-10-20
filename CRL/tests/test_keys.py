import uuid
import pytest
from redis import Redis
from datetime import datetime

from tests import config
from CRL import RedisInterface



db = Redis.from_url(config['db']['url'])


def test_many_complex():

	interface = RedisInterface(db)
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
		
		assert len(interface['sessions'][id].keys()) == len(sessions[id])