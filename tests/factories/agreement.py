import uuid

from factory import LazyFunction, SubFactory

from prozorro_cdb.api.database.store import get_mongodb
from prozorro_cdb.contracting.core.database import ContractCollection
from prozorro_cdb.violation_report.database.schema.agreement import Agreement
from tests.factories.base import BaseFactory

from .organization import ProcuringEntityFactory


class AgreementFactory(BaseFactory):
    @staticmethod
    def get_collection() -> ContractCollection:
        return get_mongodb().agreement

    class Meta:
        model = Agreement

    _id = LazyFunction(lambda: uuid.uuid4().hex)
    procuringEntity = SubFactory(ProcuringEntityFactory)
