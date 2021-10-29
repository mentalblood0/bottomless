import os
import glob
from functools import cache



def singleton(c):
	return c()


@singleton
class scripts(dict):

	def __init__(self):

		path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')

		for file_path in glob.iglob(f'{path}/**/*.lua', recursive=True):

			with open(file_path, 'rb') as f:
				content = f.read()

			file_name = os.path.basename(file_path)
			script_name = os.path.splitext(file_name)[0]
			
			self[script_name] = content


import sys
sys.modules[__name__] = scripts