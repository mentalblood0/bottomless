import json



with open('tests/config.json') as f:
    config = json.load(f)



import sys
sys.modules[__name__] = config