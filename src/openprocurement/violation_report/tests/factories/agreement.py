import uuid

from factory import Faker, LazyFunction, List, SubFactory

from openprocurement.api.database_async import get_mongodb
from openprocurement.contracting.core.database_async import ContractCollection
from openprocurement.violation_report.database.schema.tender import (
    Tender,
    TenderAgreement,
)
from openprocurement.violation_report.tests.factories.base import BaseFactory

from ...database.schema.agreement import Agreement
from .organization import BuyerFactory, ProcuringEntityFactory, SupplierFactory


class AgreementFactory(BaseFactory):

    @staticmethod
    def get_collection() -> ContractCollection:
        return get_mongodb().agreement

    class Meta:
        model = Agreement

    _id = LazyFunction(lambda : uuid.uuid4().hex)
    procuringEntity = SubFactory(ProcuringEntityFactory)