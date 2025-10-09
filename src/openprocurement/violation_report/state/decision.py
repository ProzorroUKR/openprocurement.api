from datetime import datetime

from aiohttp.web import HTTPBadRequest

from openprocurement.api.errors_async import JsonHTTPBadRequest
from openprocurement.api.models_async.document import DocumentTypes, RequestDocument
from openprocurement.violation_report.database.schema.violation_report import (
    Document,
    ViolationReportDBModel,
    ViolationReportDecisionDBModel,
    ViolationReportStatus,
)
from openprocurement.violation_report.handlers.schema.decision import (
    DecisionRequestData,
)
from openprocurement.violation_report.state.base import BaseState


class ViolationReportDecisionState(BaseState):
    @classmethod
    def validate_decision_period(
        cls,
        violation_report: ViolationReportDBModel,
        now: datetime,
    ) -> None:
        period = violation_report.defendantPeriod
        if period is None or now < period.endDate:
            raise JsonHTTPBadRequest(
                details="Can change decision only after defendantPeriod.endDate.",
                now=now,
                period=period.model_dump(mode="json"),
            )

    @classmethod
    def create_decision(
        cls,
        violation_report: ViolationReportDBModel,
        data: DecisionRequestData,
        now: datetime,
    ) -> ViolationReportDecisionDBModel:
        obj = ViolationReportDecisionDBModel(
            status=data.status,
            description=data.description,
            dateModified=now,
        )
        violation_report.decision = obj
        violation_report.dateModified = now
        violation_report.status = ViolationReportStatus(obj.status.value)
        return obj

    @classmethod
    def validate_add_document(cls, violation_report: ViolationReportDBModel, document: RequestDocument, now: datetime):
        cls.validate_decision_period(violation_report=violation_report, now=now)

        if document.documentType == DocumentTypes.violationReportSignature and any(
            d.documentType == DocumentTypes.violationReportSignature for d in violation_report.decision.documents
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

        violation_report.decision.documents.append(documents[0])  # allow post multiple ?
        violation_report.decision.dateModified = now
        violation_report.dateModified = now
        return documents[0]
