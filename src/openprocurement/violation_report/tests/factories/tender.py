import uuid

from factory import Faker, LazyFunction, List, SubFactory

from openprocurement.api.database_async import get_mongodb
from openprocurement.contracting.core.database_async import ContractCollection
from openprocurement.violation_report.database.schema.tender import (
    Tender,
    TenderAgreement,
)
from openprocurement.violation_report.tests.factories.base import BaseFactory

from .organization import BuyerFactory, SupplierFactory


class TenderAgreementFactory(BaseFactory):
    class Meta:
        model = TenderAgreement

    id = LazyFunction(lambda: uuid.uuid4().hex)


class TenderFactory(BaseFactory):

    @staticmethod
    def get_collection() -> ContractCollection:
        return get_mongodb().tender

    class Meta:
        model = Tender

    _id = LazyFunction(lambda : uuid.uuid4().hex)
    procurementMethodType = "priceQuotation"
    agreement = SubFactory(TenderAgreementFactory)
