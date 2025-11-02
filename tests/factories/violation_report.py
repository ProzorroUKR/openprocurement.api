import uuid

from factory import Factory, Faker, Iterator, LazyFunction, List, Sequence, SubFactory

from prozorro_cdb.api.database.schema.common import Period
from prozorro_cdb.api.database.schema.document import Document
from prozorro_cdb.api.database.store import get_mongodb
from prozorro_cdb.violation_report.database.collection import ViolationReportCollection
from prozorro_cdb.violation_report.database.schema.violation_report import (
    ReportDetails,
    ViolationReportDBModel,
    ViolationReportReason,
)
from tests.factories.base import BaseFactory
from tests.factories.organization import (
    BuyerFactory,
    ProcuringEntityFactory,
    SupplierFactory,
)


class DocumentFactory(Factory):
    class Meta:
        model = Document

    url = Faker("file_path")
    hash = "0" * 32

    dateModified = Faker("date_time_between", end_date="-1d")
    datePublished = Faker("date_time_between", end_date="-1d")


class ReportDetailsFactory(Factory):
    class Meta:
        model = ReportDetails

    reason = Iterator(ViolationReportReason)
    description = Faker("sentence")
    documents = List([SubFactory(DocumentFactory)])
    dateModified = Faker("date_time_between", end_date="-1d")


class PeriodFactory(Factory):
    class Meta:
        model = Period

    startDate = Faker("date_time_between", end_date="-5d")
    endDate = Faker("date_time_between", start_date="-5d")


class ViolationReportDBModelFactory(BaseFactory):
    @staticmethod
    def get_collection() -> ViolationReportCollection:
        return get_mongodb().violation_report

    class Meta:
        model = ViolationReportDBModel

    _id = Sequence(lambda n: "UA-2025-10-22-%06d" % n)
    tender_id = LazyFunction(lambda: uuid.uuid4().hex)
    contract_id = LazyFunction(lambda: uuid.uuid4().hex)
    dateCreated = Faker("date_time_between", start_date="-2d")
    datePublished = Faker("date_time_between", start_date="-2d")
    dateModified = Faker("date_time_between", start_date="-1d")
    defendantPeriod = SubFactory(PeriodFactory)
    details = SubFactory(ReportDetailsFactory)
    author = SubFactory(BuyerFactory)
    defendants = List([SubFactory(SupplierFactory)])
    authority = SubFactory(ProcuringEntityFactory)
