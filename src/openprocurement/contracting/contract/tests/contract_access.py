from openprocurement.api.tests.base import snitch
from openprocurement.contracting.contract.tests.contract_access_blanks import (
    generate_credentials,
    generate_credentials_invalid,
    get_credentials,
)
from openprocurement.contracting.core.tests.base import BaseContractWebTest


class ContractResourceCredentialsTest(BaseContractWebTest):
    def setUp(self):
        super().setUp()
        self.tender_token = self.tender_document["owner_token"]

    test_get_credentials = snitch(get_credentials)
    test_generate_credentials_invalid = snitch(generate_credentials_invalid)


class ContractActiveResourceCredentialsTest(BaseContractWebTest):
    initial_status = "active"

    def setUp(self):
        super().setUp()
        self.tender_token = self.tender_document["owner_token"]
        self.set_status(self.initial_status)

    test_generate_credentials = snitch(generate_credentials)
