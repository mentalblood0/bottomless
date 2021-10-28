import pytest

from tests import config
from bottomless import RedisInterface



def test_basic():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface |= {
		'1': {
			'1': {
				'1': 'one.one.one'
			},
			'2': 'one.two'
		},
		'2': 'two'
	}

	assert interface() == {
		'1': {
			'1': {
				'1': 'one.one.one'
			},
			'2': 'one.two'
		},
		'2': 'two'
	}


def test_not_dict():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	key = 1

	interface[key] = False
	assert interface[key]() == False

	interface[key] = {
		'a': 1,
		'b': 2
	}
	assert interface.db.get(interface[key].key) == None
	assert interface[key]() == {
		'a': 1,
		'b': 2
	}

	interface[key] = False
	assert interface[key]() == False


def test_deep_dict_shallow_update():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	key = 'key'
	deep = {
		'a': {
			'b': 2
		},
		'c': {
			'd': 4
		},
		'f': {
			'g': 7
		}
	}
	shallow = {
		'a': {
			'e': 5
		},
		'c': 3
	}

	interface[key] = deep
	assert interface[key]() == deep

	interface[key] |= shallow
	print(interface[key]())
	assert interface[key]() == deep | shallow