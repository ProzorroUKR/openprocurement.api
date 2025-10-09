from datetime import datetime

from aiohttp.web import HTTPBadRequest

from openprocurement.api.errors_async import JsonHTTPBadRequest
from openprocurement.api.models_async.document import DocumentTypes, RequestDocument
from openprocurement.violation_report.database.schema.violation_report import (
    DefendantStatementDBModel,
    Document,
    ViolationReportDBModel,
)
from openprocurement.violation_report.handlers.schema.defendant_statement import (
    DefendantStatementRequestData,
)
from openprocurement.violation_report.state.base import BaseState


class ViolationReportDefendantState(BaseState):
    @classmethod
    def validate_defendant_period(
        cls,
        violation_report: ViolationReportDBModel,
        now: datetime,
    ) -> None:
        period = violation_report.defendantPeriod
        if period is None or not (period.startDate < now <= period.endDate):
            raise JsonHTTPBadRequest(
                details="Can add defendantStatement only during defendantPeriod.",
                now=now,
                period=period.model_dump(mode="json"),
            )

    @classmethod
    def create_defendant_statement(
        cls, violation_report: ViolationReportDBModel, data: DefendantStatementRequestData, now: datetime
    ) -> DefendantStatementDBModel:
        obj = DefendantStatementDBModel(
            description=data.description,
            dateModified=now,
        )
        violation_report.defendantStatement = obj
        violation_report.dateModified = now
        return obj

    @classmethod
    def validate_add_document(cls, violation_report: ViolationReportDBModel, document: RequestDocument, now: datetime):
        cls.validate_defendant_period(violation_report=violation_report, now=now)

        if document.documentType == DocumentTypes.violationReportSignature and any(
            d.documentType == DocumentTypes.violationReportSignature
            for d in violation_report.defendantStatement.documents
        ):
            raise HTTPBadRequest(text="Signature document already exists. Update it with PUT method instead.")

    @classmethod
    def add_document(
        cls,
        violation_report: ViolationReportDBModel,
        document: RequestDocument,
        base_url: str,
        now: datetime,
    ) -> Document:
        documents = cls.create_document_objects(now, base_url, [document])

        violation_report.defendantStatement.documents.append(documents[0])  # allow post multiple ?
        violation_report.defendantStatement.dateModified = now
        violation_report.dateModified = now
        return documents[0]
