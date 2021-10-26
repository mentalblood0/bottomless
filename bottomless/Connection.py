class Connection(dict):

	def __eq__(self, other):
		return all([
			self[k] == other[k]
			for k in [
				'host',
				'port',
				'db'
			]
		])



import sys
sys.modules[__name__] = Connection