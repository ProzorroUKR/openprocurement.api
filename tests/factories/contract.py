import uuid

from factory import LazyFunction, List, SubFactory

from prozorro_cdb.api.database.store import get_mongodb
from prozorro_cdb.contracting.core.database import ContractCollection
from prozorro_cdb.violation_report.database.schema.contract import Contract
from tests.factories.base import BaseFactory

from .organization import BuyerFactory, SupplierFactory


class ContractFactory(BaseFactory):
    @staticmethod
    def get_collection() -> ContractCollection:
        return get_mongodb().contract

    class Meta:
        model = Contract

    _id = LazyFunction(lambda: uuid.uuid4().hex)
    tender_id = LazyFunction(lambda: uuid.uuid4().hex)
    buyer = SubFactory(BuyerFactory)
    suppliers = List([SubFactory(SupplierFactory)])
