rm -rf dist CRL/CRL.egg-info
python3.9 -m build -n
python3.9 -m pip install --force-reinstall dist/CRL-0.1.0-py3-none-any.whl