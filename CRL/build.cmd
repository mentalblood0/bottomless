rd /s /q -rf dist CRL\CRL.egg-info
py -m build -n
py -m pip install --force-reinstall dist\CRL-0.2.0-py3-none-any.whl