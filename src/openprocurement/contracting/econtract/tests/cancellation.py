from openprocurement.api.tests.base import snitch
from openprocurement.contracting.econtract.tests.base import BaseEContractContentWebTest
from openprocurement.contracting.econtract.tests.cancellation_blanks import (
    create_cancellation_by_buyer,
    create_cancellation_by_supplier,
    get_cancellation,
)


class ContractCancellationTest(BaseEContractContentWebTest):
    test_create_cancellation_by_buyer = snitch(create_cancellation_by_buyer)
    test_create_cancellation_by_supplier = snitch(create_cancellation_by_supplier)
    test_get_cancellation = snitch(get_cancellation)
