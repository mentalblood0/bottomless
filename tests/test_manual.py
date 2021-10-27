import pytest
from redis import Redis

from tests import config



def test_transaction():

	r = Redis.from_url(config['db']['url'])
	r.set('OUR-SEQUENCE-KEY', '0')

	def client_side_incr(pipe):
		current_value = pipe.get('OUR-SEQUENCE-KEY')
		next_value = int(current_value) + 1
		pipe.multi()
		pipe.set('OUR-SEQUENCE-KEY', next_value)

	r.transaction(client_side_incr, 'OUR-SEQUENCE-KEY')
	assert r.get('OUR-SEQUENCE-KEY') == b'1'