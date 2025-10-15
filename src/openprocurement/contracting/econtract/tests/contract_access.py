from openprocurement.api.tests.base import snitch
from openprocurement.contracting.econtract.tests.base import BaseEContractWebTest
from openprocurement.contracting.econtract.tests.contract_access_blanks import (
    generate_access,
    get_access,
)
from openprocurement.contracting.econtract.tests.data import test_econtract_data


class ContractAccessResourceTest(BaseEContractWebTest):
    initial_contract_data = test_econtract_data

    test_generate_access = snitch(generate_access)
    test_get_access = snitch(get_access)
