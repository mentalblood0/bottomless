def RedisInterfaceIterator(interface):

	for k in sorted(interface.keys()):
		yield interface[k]()



import sys
sys.modules[__name__] = RedisInterfaceIterator