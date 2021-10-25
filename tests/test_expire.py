import pytest
from time import sleep

from tests import config
from bottomless import RedisInterface



def test_append():

	interface = RedisInterface(config['db']['url'])
	interface.clear()

	interface['key'] = 'value'
	interface['key'].expire(1)

	sleep(1)

	assert interface['key']() == None