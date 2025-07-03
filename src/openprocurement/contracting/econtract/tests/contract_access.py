from openprocurement.api.tests.base import snitch
from openprocurement.contracting.core.procedure.models.access import AccessRole
from openprocurement.contracting.core.tests.utils import create_contract
from openprocurement.contracting.econtract.tests.base import BaseEContractWebTest
from openprocurement.contracting.econtract.tests.contract_access_blanks import (
    generate_access,
    get_access,
)
from openprocurement.contracting.econtract.tests.data import test_econtract_data


class ContractAccessResourceTest(BaseEContractWebTest):
    initial_data = test_econtract_data

    def create_contract(self):
        for tender_contract in self.tender_document.get("contracts", ""):
            contract = self.initial_data
            contract.update(tender_contract)
            contract.update(
                {
                    "tender_id": self.tender_id,
                    "access": [
                        {"owner": "broker", "role": AccessRole.SUPPLIER},
                        {
                            "owner": self.tender_document["owner"],
                            "role": AccessRole.BUYER,
                        },
                    ],
                }
            )
            self.contract_id = contract["id"]
            self.contract = create_contract(self, contract)

    test_generate_access = snitch(generate_access)
    test_get_access = snitch(get_access)
