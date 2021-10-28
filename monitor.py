import redis        



class Monitor():

	def __init__(self, connection_pool):
		self.connection_pool = connection_pool
		self.connection = None

	def monitor(self):

		if self.connection is None:
			self.connection = self.connection_pool.get_connection(
				'monitor', None)
		self.connection.send_command("monitor")
		
		return self.listen()

	def parse_response(self):
		return self.connection.read_response()

	def listen(self):
		while True:
			try:
				yield self.parse_response().decode()
			except:
				break


if  __name__ == '__main__':

	pool = redis.ConnectionPool(host='10.8.5.170', port=6379, db=0)
	monitor = Monitor(pool)
	commands = monitor.monitor()

	for c in commands:
		# print(c[c.find('"'):].split(' ')[0].replace('"', ''))
		print(c[c.find('"'):].replace('"', '').split(' '))