from functools import cache
from os.path import dirname, join, abspath



@cache
def get(name):
	
	filename = join(dirname(abspath(__file__)), 'scripts', f'{name}.lua')
	
	with open(filename, 'rb') as f:
		content = f.read()
	
	return content