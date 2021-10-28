import pytest

from tests import config
from bottomless import RedisInterface



def test_all():

	interface = RedisInterface(config['db']['url'])

	private_with_getters = [
		'db',
		'connection',
		'key',
		'path',
		'default_type',
		'pathToKey',
		'keyToPath',
		'prefixes_types',
		'types_prefixes',
	]

	private_without_getters = [
		'pipeline'
	]

	for name in private_with_getters:
		with pytest.raises(AttributeError):
			setattr(interface, name, 'lalala')
	
	for name in private_with_getters + private_without_getters:
		with pytest.raises(AttributeError):
			getattr(interface, f'__{name}')