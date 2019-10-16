import json
import os.path
from openprocurement.tender.core.tests.base import BaseWebTest

here = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(here, "data/agreement.json")) as _in:
    TEST_AGREEMENT = json.load(_in)


class BaseAgreementTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
    docservice = False
