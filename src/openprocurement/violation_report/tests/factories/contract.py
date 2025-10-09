import uuid

from factory import Faker, LazyFunction, List, SubFactory

from openprocurement.api.database_async import get_mongodb
from openprocurement.contracting.core.database_async import ContractCollection
from openprocurement.violation_report.database.schema.contract import Contract
from openprocurement.violation_report.tests.factories.base import BaseFactory

from .organization import BuyerFactory, SupplierFactory


class ContractFactory(BaseFactory):

    @staticmethod
    def get_collection() -> ContractCollection:
        return get_mongodb().contract

    class Meta:
        model = Contract

    _id = LazyFunction(lambda : uuid.uuid4().hex)
    tender_id = Faker("uuid4")
    buyer = SubFactory(BuyerFactory)
    suppliers = List([SubFactory(SupplierFactory)])
