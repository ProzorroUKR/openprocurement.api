from typing import Optional

from prozorro_cdb.api.context import get_now_async
from prozorro_cdb.api.database.schema.document import Document, DocumentTypes
from prozorro_cdb.api.errors import JsonHTTPBadRequest
from prozorro_cdb.api.handlers.schema.document import PostDocument
from prozorro_cdb.api.state.base import BaseState
from prozorro_cdb.violation_report.database.schema.violation_report import (
    DefendantStatementDBModel,
    DraftActiveObjectStatus,
    ViolationReportDBModel,
)
from prozorro_cdb.violation_report.handlers.schema.defendant_statement import (
    DefendantStatementPatchRequestData,
    DefendantStatementPostRequestData,
)
from prozorro_cdb.violation_report.handlers.schema.document import PatchDocument


class ViolationReportDefendantState(BaseState):
    @classmethod
    def validate_create(
        cls,
        violation_report: ViolationReportDBModel,
    ) -> None:
        cls.validate_no_active_objects(violation_report)
        cls.validate_defendant_period(violation_report)

    @classmethod
    def validate_no_active_objects(
        cls,
        violation_report: ViolationReportDBModel,
    ) -> None:
        if any(d.status == DraftActiveObjectStatus.active for d in violation_report.defendantStatements):
            raise JsonHTTPBadRequest(details="Defendant statement is active.")

    @classmethod
    def validate_defendant_period(
        cls,
        violation_report: ViolationReportDBModel,
    ) -> None:
        now = get_now_async()
        period = violation_report.defendantPeriod
        if period is None or not (period.startDate < now <= period.endDate):
            raise JsonHTTPBadRequest(
                details="Can add defendantStatement only during defendantPeriod.",
                now=now,
                period=period and period.model_dump(mode="json"),
            )

    @classmethod
    def create_defendant_statement(
        cls,
        uid: str,
        base_url: str,
        violation_report: ViolationReportDBModel,
        data: DefendantStatementPostRequestData,
    ) -> DefendantStatementDBModel:
        now = get_now_async()
        obj = DefendantStatementDBModel(
            id=uid,
            dateModified=now,
            description=data.description,
            documents=cls.create_document_objects(now, base_url, data.documents),
        )
        violation_report.defendantStatements.append(obj)
        return obj

    @classmethod
    def validate_update_defendant_statement(
        cls, violation_report: ViolationReportDBModel, defendant_statement: DefendantStatementDBModel
    ):
        cls.validate_no_active_objects(violation_report)
        cls.validate_defendant_period(violation_report=violation_report)
        cls.validate_defendant_statement_draft(defendant_statement=defendant_statement)

    @classmethod
    def update_defendant_statement(
        cls,
        defendant_statement: DefendantStatementDBModel,
        data: DefendantStatementPatchRequestData,
    ) -> Optional[DefendantStatementDBModel]:
        if defendant_statement.description != data.description:
            defendant_statement.description = data.description
            defendant_statement.dateModified = get_now_async()
            return defendant_statement
        return None

    @classmethod
    def validate_publish_defendant_statement(
        cls,
        violation_report: ViolationReportDBModel,
        defendant_statement: DefendantStatementDBModel,
    ):
        cls.validate_update_defendant_statement(violation_report, defendant_statement)
        # there could be more checks (like signature) later

    @classmethod
    def publish_defendant_statement(
        cls,
        violation_report: ViolationReportDBModel,
        defendant_statement: DefendantStatementDBModel,
    ) -> None:
        now = get_now_async()

        defendant_statement.status = DraftActiveObjectStatus.active
        defendant_statement.datePublished = now
        violation_report.dateModified = now

    @classmethod
    def validate_defendant_statement_draft(cls, defendant_statement: DefendantStatementDBModel):
        if defendant_statement.status != DraftActiveObjectStatus.draft:
            raise JsonHTTPBadRequest(details="Only allowed in status `draft`.")

    @classmethod
    def validate_post_document(
        cls,
        violation_report: ViolationReportDBModel,
        defendant_statement: DefendantStatementDBModel,
        document: PostDocument,
    ):
        cls.validate_update_defendant_statement(violation_report, defendant_statement)

        if document.documentType == DocumentTypes.violationReportSignature and any(
            d.documentType == DocumentTypes.violationReportSignature for d in defendant_statement.documents
        ):
            raise JsonHTTPBadRequest(details="Signature document already exists. Update it with PUT method instead.")

    @classmethod
    def post_document(
        cls,
        defendant_statement: DefendantStatementDBModel,
        document: PostDocument,
        base_url: str,
    ) -> Document:
        now = get_now_async()
        documents = cls.create_document_objects(now, base_url, [document])
        defendant_statement.documents.append(documents[0])  # allow post multiple ?
        defendant_statement.dateModified = now
        return documents[0]

    @classmethod
    def patch_document(
        cls,
        defendant_statement: DefendantStatementDBModel,
        document: Document,
        doc_index: int,
        updates: PatchDocument,
    ) -> Optional[Document]:
        changes = updates.model_dump(exclude_none=True)
        updated_document = document.model_copy(update=changes)
        if document != updated_document:
            defendant_statement.documents[doc_index] = updated_document  # update document

            now = get_now_async()
            updated_document.dateModified = now
            defendant_statement.dateModified = now
            return updated_document
        return None

    @classmethod
    def put_document(
        cls,
        defendant_statement: DefendantStatementDBModel,
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
        defendant_statement.documents.append(new_document)

        defendant_statement.dateModified = now
        return new_document

    @classmethod
    def delete_document(
        cls,
        defendant_statement: DefendantStatementDBModel,
        document_id: str,
    ) -> Optional[DefendantStatementDBModel]:
        doc_len = len(defendant_statement.documents)
        defendant_statement.documents = [d for d in defendant_statement.documents if d.id != document_id]
        if doc_len != len(defendant_statement.documents):
            defendant_statement.dateModified = get_now_async()
            return defendant_statement
        return None
