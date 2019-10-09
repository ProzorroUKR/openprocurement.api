import json
import uuid
import os.path
from copy import deepcopy
from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.base import BaseWebTest, change_auth

here = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(here, "data/agreement.json")) as _in:
    TEST_AGREEMENT = json.load(_in)


class BaseAgreementTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
    docservice = False
