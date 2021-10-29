import os
from distutils.core import setup



if __name__ == '__main__':

	long_description = ''
	if os.path.exists('README.md'):
		with open('README.md', encoding='utf-8') as f:
			long_description = f.read()

	setup(
		name='bottomless',
		version='0.3.0',
		description='Correct Redis Library',
		long_description=long_description,
		long_description_content_type='text/markdown',
		author='mentalblood',
		install_requires=[
			'redis',
			'flatten-dict'
		],
		packages=['bottomless']
	)