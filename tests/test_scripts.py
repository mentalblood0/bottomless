import pytest

from tests import config
from bottomless import RedisInterface



def test_getByPattern():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface['key'] = {
		'a': {
			'b': 2
		},
		'c': 3
	}

	keys, values = interface._getByPattern('key*')
	assert sorted(keys) == [b'key.a.b', b'key.c']
	assert sorted(values) == [b'i2', b'i3']