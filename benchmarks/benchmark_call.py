from sharpener import Benchmark

from tests import config
from bottomless import RedisInterface



class simple(Benchmark):

	def prepare(self, keys_number):

		self.interface = RedisInterface(config['db']['url'])
		self.interface.clear()
	
		self.interface |= {
			i+1: i+1
			for i in range(keys_number)
		}
	
	def run(self, **kwargs):
		self.interface()
	
	def clean(self, **kwargs):
		self.interface.clear()


class realistic(Benchmark):
	
	def prepare(self, commands_number):

		interface = RedisInterface(config['db']['url'])
		interface.clear()

		self.commands = interface['commands']

		self.commands += [{
			'id': str(i),
			'command': {
				'id': 'lalala',
				'name': 'connect',
				'type': 'cmdConnect',
				'protocol': 't0'
			},
			'answer': {
				'type': 'ansOk'
			},
			'answer_sent': 0
		} for i in range(commands_number)]

		self.result = []

	def run(self, **kwargs):

		for c in self.commands:
			if not c['answer_sent']():
				answer = c['answer']()
				if answer != None:
					answer = answer | {'commandId': c['id']()}
					self.result.append(answer)
	
	def clean(self, **kwargs):
		self.commands.clear()