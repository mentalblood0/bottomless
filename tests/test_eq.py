import pytest

from tests import config
from CRL import RedisInterface



def test_valid_key():

	interface = RedisInterface(config['db']['url'])
	interface['key'] = 'value'

	assert interface['key'] == 'value'


def test_invalid_key():

	interface = RedisInterface(config['db']['url'])
	del interface['key']

	assert interface['key'] == None