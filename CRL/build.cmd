rd /s /q -rf dist CRL\CRL.egg-info
py -m build -n
py -m pip install --force-reinstall dist\CRL-0.2.1-py3-none-any.whl