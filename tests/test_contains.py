import pytest

from tests import config
from bottomless import RedisInterface



def test_basic():

	interface = RedisInterface(config['db']['url'])
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