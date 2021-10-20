import uuid
import pytest
from redis import Redis
from datetime import datetime

from tests import config
from CRL import RedisInterface



db = Redis.from_url(config['db']['url'])


def test_basic():

	interface = RedisInterface(db)
	interface.clear()

	interface |= {
		'sessions': {
			1: {
				'name': 'one'
			},
			'2': {
				'name': 'two'
			}
		}
	}

	assert 1 in interface['sessions']
	assert '1' in interface['sessions']
	
	assert 2 in interface['sessions']
	assert '2' in interface['sessions']