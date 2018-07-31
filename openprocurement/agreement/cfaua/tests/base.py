import os.path
import json


here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, 'data/agreement.json')) as _in:
    TEST_AGREEMENT = json.load(_in)
