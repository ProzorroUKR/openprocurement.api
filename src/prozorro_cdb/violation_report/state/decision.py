from typing import Optional

from aiohttp.web import HTTPBadRequest

from prozorro_cdb.api.context import get_now_async
from prozorro_cdb.api.database.schema.document import Document, DocumentTypes
from prozorro_cdb.api.errors import JsonHTTPBadRequest
from prozorro_cdb.api.handlers.schema.document import PatchDocument, PostDocument
from prozorro_cdb.api.state.base import BaseState
from prozorro_cdb.violation_report.database.schema.violation_report import (
    DecisionDBModel,
    DraftActiveObjectStatus,
    ViolationReportDBModel,
    ViolationReportResolution,
    ViolationReportStatus,
)
from prozorro_cdb.violation_report.handlers.schema.decision import (
    DecisionPatchRequestData,
    DecisionPostRequestData,
)


class ViolationReportDecisionState(BaseState):
    @classmethod
    def validate_create(
        cls,
        violation_report: ViolationReportDBModel,
    ) -> None:
        cls.validate_no_active_objects(violation_report)
        cls.validate_decision_period(violation_report)

    @classmethod
    def validate_no_active_objects(
        cls,
        violation_report: ViolationReportDBModel,
    ) -> None:
        if any(d.status == DraftActiveObjectStatus.active for d in violation_report.decisions):
            raise JsonHTTPBadRequest(details="Decision is active.")

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
                period=period and period.model_dump(mode="json"),
            )

    @classmethod
    def create_decision(
        cls,
        uid: str,
        base_url: str,
        violation_report: ViolationReportDBModel,
        data: DecisionPostRequestData,
    ) -> DecisionDBModel:
        now = get_now_async()
        obj = DecisionDBModel(
            id=uid,
            dateModified=now,
            resolution=data.resolution,
            description=data.description,
            documents=cls.create_document_objects(now, base_url, data.documents),
        )
        violation_report.decisions.append(obj)
        return obj

    @classmethod
    def validate_update_decision(cls, violation_report: ViolationReportDBModel, decision: DecisionDBModel):
        cls.validate_no_active_objects(violation_report)
        cls.validate_decision_period(violation_report=violation_report)
        cls.validate_decision_draft(decision=decision)

    @classmethod
    def update_decision(
        cls,
        decision: DecisionDBModel,
        data: DecisionPatchRequestData,
    ) -> Optional[DecisionDBModel]:
        is_changed = False

        if decision.description != data.description:
            decision.description = data.description
            is_changed = True

        if decision.resolution != data.resolution:
            decision.resolution = data.resolution
            is_changed = True

        if is_changed:
            decision.dateModified = get_now_async()
            return decision

        return None

    @classmethod
    def validate_publish_decision(
        cls,
        violation_report: ViolationReportDBModel,
        decision: DecisionDBModel,
    ):
        cls.validate_update_decision(violation_report, decision)

        # validate both evidence and signature documents provided
        documents = {d.documentType: d for d in decision.documents}
        if DocumentTypes.violationReportSignature not in documents:
            raise JsonHTTPBadRequest(details="Signature document not found.")

        signature = documents[DocumentTypes.violationReportSignature]  # gets the latest signature
        if signature.dateModified < decision.dateModified:
            raise JsonHTTPBadRequest(details="Signature document should be updated.")

    @classmethod
    def publish_decision(
        cls,
        violation_report: ViolationReportDBModel,
        decision: DecisionDBModel,
    ) -> None:
        now = get_now_async()

        decision.status = DraftActiveObjectStatus.active
        decision.datePublished = now

        violation_report.status = (
            ViolationReportStatus.satisfied
            if decision.resolution == ViolationReportResolution.satisfied
            else ViolationReportStatus.declined
        )
        violation_report.dateModified = now

    @classmethod
    def validate_decision_draft(cls, decision: DecisionDBModel):
        if decision.status != DraftActiveObjectStatus.draft:
            raise JsonHTTPBadRequest(details="Only allowed in status `draft`.")

    @classmethod
    def validate_post_document(
        cls, violation_report: ViolationReportDBModel, decision: DecisionDBModel, document: PostDocument
    ):
        cls.validate_update_decision(violation_report, decision)

        if document.documentType == DocumentTypes.violationReportSignature and any(
            d.documentType == DocumentTypes.violationReportSignature for d in decision.documents
        ):
            raise HTTPBadRequest(text="Signature document already exists. Update it with PUT method instead.")

    @classmethod
    def post_document(
        cls,
        decision: DecisionDBModel,
        document: PostDocument,
        base_url: str,
    ) -> Document:
        now = get_now_async()
        documents = cls.create_document_objects(now, base_url, [document])

        decision.documents.append(documents[0])  # allow post multiple ?
        decision.dateModified = now
        return documents[0]

    @classmethod
    def patch_document(
        cls,
        decision: DecisionDBModel,
        document: Document,
        doc_index: int,
        updates: PatchDocument,
    ) -> Optional[Document]:
        changes = updates.model_dump(exclude_none=True)
        updated_document = document.model_copy(update=changes)
        if document != updated_document:
            decision.documents[doc_index] = updated_document  # update document

            now = get_now_async()
            updated_document.dateModified = now
            decision.dateModified = now
            return updated_document
        return None

    @classmethod
    def put_document(
        cls,
        decision: DecisionDBModel,
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
        update = documents[0].model_dump(exclude={"id", "author", "documentType"})

        new_document = document.model_copy(update=update)
        decision.documents.append(new_document)

        decision.dateModified = now
        return new_document

    @classmethod
    def delete_document(
        cls,
        decision: DecisionDBModel,
        document_id: str,
    ) -> Optional[DecisionDBModel]:
        doc_len = len(decision.documents)
        decision.documents = [d for d in decision.documents if d.id != document_id]
        if doc_len != len(decision.documents):
            decision.dateModified = get_now_async()
            return decision
        return None
