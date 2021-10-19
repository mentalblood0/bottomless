def RedisInterfaceIterator(interface):

	for k in sorted(interface.keys()):
		yield interface[k]._get()



import sys
sys.modules[__name__] = RedisInterfaceIterator