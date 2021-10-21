import pytest

from tests import config
from bottomless import RedisInterface



def test_valid_key():

	interface = RedisInterface(config['db']['url'])
	interface['key'] = 'value'

	del interface['key']


def test_cascade():

	interface = RedisInterface(config['db']['url'])

	interface['1'] = 'one'
	interface['2'] = 'two'
	interface['1']['1'] = 'one.one'
	interface['1']['2'] = 'one.two'
	interface['11'] = 'oneone'

	del interface['1']

	assert interface['1']() == None
	assert interface['1'] == None
	assert interface['1']['1'] == None
	assert interface['1']['2'] == None
	assert interface['11'] == 'oneone'

	del interface['2']

	assert interface['2'] == None