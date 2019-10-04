import json
import uuid
import os.path
from copy import deepcopy
from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.base import BaseWebTest, change_auth

here = os.path.dirname(os.path.abspath(__file__))
now = get_now()
with open(os.path.join(here, "data/agreement.json")) as _in:
    TEST_AGREEMENT = json.load(_in)


class BaseAgreementTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
    initial_auth = ("Basic", ("token", ""))
    docservice = False


class BaseAgreementWebTest(BaseAgreementTest):
    relative_to = os.path.dirname(__file__)
    initial_data = TEST_AGREEMENT

    def setUp(self):
        super(BaseAgreementWebTest, self).setUp()
        self.create_agreement()

    def tearDown(self):
        del self.db[self.agreement_id]
        super(BaseAgreementWebTest, self).tearDown()

    def create_agreement(self):
        data = deepcopy(self.initial_data)
        data["id"] = uuid.uuid4().hex
        with change_auth(self.app, ("Basic", ("agreements", ""))) as app:
            response = self.app.post_json("/agreements", {"data": data})
        agreement = response.json["data"]
        self.agreement_token = response.json["access"]["token"]
        self.agreement_id = agreement["id"]


class BaseDSAgreementWebTest(BaseAgreementWebTest):
    docservice = True
