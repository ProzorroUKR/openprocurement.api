import json
import os.path
from copy import deepcopy
from datetime import datetime
from hashlib import sha512
from uuid import uuid4

from openprocurement.api.utils import get_now

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "data/agreement.json")) as _in:
    TEST_AGREEMENT = json.load(_in)


with open(os.path.join(here, "data/documents.json")) as _in:
    TEST_DOCUMENTS = json.load(_in)


with open(os.path.join(here, "data/features.json")) as _in:
    TEST_FEATURES = json.load(_in)

with open(os.path.join(here, "data/change.json")) as _in:
    TEST_CHANGE = json.load(_in)

now = datetime.now()
test_tender_token = uuid4().hex
test_agreement_data = deepcopy(TEST_AGREEMENT)
test_agreement_data_wo_items = deepcopy(test_agreement_data)

test_agreement_data["dateSigned"] = get_now().isoformat()
test_agreement_data["tender_token"] = sha512(test_tender_token.encode()).hexdigest()

del test_agreement_data_wo_items["items"]
