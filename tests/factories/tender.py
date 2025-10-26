import uuid

from factory import Factory, LazyFunction, SubFactory

from prozorro_cdb.api.database.store import get_mongodb
from prozorro_cdb.contracting.core.database import ContractCollection
from prozorro_cdb.violation_report.database.schema.tender import Tender, TenderAgreement
from tests.factories.base import BaseFactory


class TenderAgreementFactory(Factory):
    class Meta:
        model = TenderAgreement

    id = LazyFunction(lambda: uuid.uuid4().hex)


class TenderFactory(BaseFactory):
    @staticmethod
    def get_collection() -> ContractCollection:
        return get_mongodb().tender

    class Meta:
        model = Tender

    _id = LazyFunction(lambda: uuid.uuid4().hex)
    procurementMethodType = "priceQuotation"
    agreement = SubFactory(TenderAgreementFactory)
