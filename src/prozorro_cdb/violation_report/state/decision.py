from typing import Optional

from aiohttp.web import HTTPBadRequest

from prozorro_cdb.api.context import get_now_async
from prozorro_cdb.api.database.schema.document import Document, DocumentTypes
from prozorro_cdb.api.errors import JsonHTTPBadRequest
from prozorro_cdb.api.handlers.schema.document import PatchDocument, PostDocument
from prozorro_cdb.api.state.base import BaseState
from prozorro_cdb.violation_report.database.schema.violation_report import (
    ViolationReportDBModel,
    ViolationReportDecisionDBModel,
    ViolationReportStatus,
)
from prozorro_cdb.violation_report.handlers.schema.decision import DecisionRequestData


class ViolationReportDecisionState(BaseState):
    @classmethod
    def validate_decision_period(
        cls,
        violation_report: ViolationReportDBModel,
    ) -> None:
        period = violation_report.defendantPeriod
        now = get_now_async()
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
    ) -> ViolationReportDecisionDBModel:
        now = get_now_async()
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
    def validate_post_document(cls, violation_report: ViolationReportDBModel, document: PostDocument):
        cls.validate_decision_period(violation_report=violation_report)

        if document.documentType == DocumentTypes.violationReportSignature and any(
            d.documentType == DocumentTypes.violationReportSignature for d in violation_report.decision.documents
        ):
            raise HTTPBadRequest(text="Signature document already exists. Update it with PUT method instead.")

    @classmethod
    def post_document(
        cls,
        violation_report: ViolationReportDBModel,
        document: PostDocument,
        base_url: str,
    ) -> Document:
        now = get_now_async()
        documents = cls.create_document_objects(now, base_url, [document])

        violation_report.decision.documents.append(documents[0])  # allow post multiple ?
        violation_report.decision.dateModified = now
        violation_report.dateModified = now
        return documents[0]

    @classmethod
    def patch_document(
        cls,
        violation_report: ViolationReportDBModel,
        document: Document,
        doc_index: int,
        updates: PatchDocument,
    ) -> Optional[Document]:
        changes = updates.model_dump(exclude_none=True)
        updated_document = document.model_copy(update=changes)
        if document != updated_document:
            violation_report.decision.documents[doc_index] = updated_document  # update document

            now = get_now_async()
            updated_document.dateModified = now
            violation_report.decision.dateModified = now
            violation_report.dateModified = now
            return updated_document
        return None

    @classmethod
    def put_document(
        cls,
        violation_report: ViolationReportDBModel,
        base_url: str,
        document_data: PostDocument,
        document: Document,
    ) -> Document:
        now = get_now_async()
        documents = cls.create_document_objects(
            now=now,
            base_url=base_url,
            documents=[document_data],
        )
        update = documents[0].model_dump(exclude={"id", "author", "format", "documentType"})

        new_document = document.model_copy(update=update)
        violation_report.decision.documents.append(new_document)

        violation_report.decision.dateModified = now
        violation_report.dateModified = now
        return new_document
