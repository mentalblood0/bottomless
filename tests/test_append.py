import pytest

from tests import config
from bottomless import RedisInterface



def test_append():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface['key'] = 'value'
	interface['another_key'] = 'another_value'
	initial_length = len(interface)

	l = 10
	m = [i for i in range(l)]
	interface += m

	assert len(interface) == len(m) + initial_length

	for i in range(len(m)):
		assert interface[i + initial_length] == m[i]