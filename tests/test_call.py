import pytest

from tests import config
from bottomless import RedisInterface



def test_nonexistent_key():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	assert interface['key'] == None
	assert interface['key']() == None


def test_deep():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface['1'] = 'one'
	interface['2'] = 'two'
	interface['1']['1']['1'] = 'one.one.one'
	interface['1']['2'] = 'one.two'

	assert interface() == {
		'1': {
			'1': {
				'1': 'one.one.one'
			},
			'2': 'one.two'
		},
		'2': 'two'
	}


def test_change_depth():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface['key'] = {
		'a': 1
	}
	interface['key']['a'] = {
		'b': 2
	}

	interface.db.get(interface['key']['a'].key) == None
	assert interface['key']() == {
		'a': {
			'b': 2
		}
	}