from typing import Optional

from openprocurement.tender.core.utils import calculate_tender_full_date
from prozorro_cdb.api.context import get_now_async
from prozorro_cdb.api.database.schema.common import Period
from prozorro_cdb.api.database.schema.document import Document, DocumentTypes
from prozorro_cdb.api.errors import JsonHTTPBadRequest
from prozorro_cdb.api.handlers.schema.document import PostDocument
from prozorro_cdb.api.state.base import BaseState
from prozorro_cdb.violation_report.constants import DEFENDANT_PERIOD_TD
from prozorro_cdb.violation_report.database.schema.agreement import Agreement
from prozorro_cdb.violation_report.database.schema.contract import Contract
from prozorro_cdb.violation_report.database.schema.tender import Tender
from prozorro_cdb.violation_report.database.schema.violation_report import (
    ReportDetails,
    ViolationReportDBModel,
    ViolationReportStatus,
)
from prozorro_cdb.violation_report.handlers.schema.document import PatchDocument
from prozorro_cdb.violation_report.handlers.schema.violation_report import (
    ViolationReportPatchDetailsRequestData,
    ViolationReportPostRequestData,
)


class ViolationReportDetailsState(BaseState):
    @classmethod
    def validate_create(
        cls,
        request_data: ViolationReportPostRequestData,
    ) -> None:
        details = request_data.details

        signatures = [d for d in details.documents if d.documentType == DocumentTypes.violationReportSignature]
        if len(signatures) > 1:
            raise JsonHTTPBadRequest(details="More than one signature document found.")

    @staticmethod
    def validate_documents_before_publish(details: ReportDetails):
        # validate evidence documents are provided (signature is not required)
        if not any(d.documentType == DocumentTypes.violationReportEvidence for d in details.documents):
            raise JsonHTTPBadRequest(details="Evidence document not found.")

    @staticmethod
    def build_defendant_period(published_date, tender: Tender) -> Period:
        # to test real periods with accelerated tenders
        defendant_period_end = calculate_tender_full_date(
            date_obj=published_date,
            timedelta_obj=DEFENDANT_PERIOD_TD,
            working_days=True,
            tender=tender.model_dump(include={"procurementMethodDetails"}),
        )
        defendant_period = Period(
            startDate=published_date,
            endDate=defendant_period_end,
        )
        return defendant_period

    @classmethod
    def create_object(
        cls,
        uid: str,
        pretty_id: str,
        base_url: str,
        request_data: ViolationReportPostRequestData,
        contract: Contract,
        tender: Tender,
        agreement: Agreement,
    ) -> ViolationReportDBModel:
        now = get_now_async()
        create_obj = ViolationReportDBModel.model_validate(
            dict(
                _id=uid,
                violationReportID=pretty_id,
                contract_id=contract.id,
                tender_id=contract.tender_id,
                author=contract.buyer,
                defendants=contract.suppliers,
                authority=agreement.procuringEntity,
                mode=tender.mode,
                status=request_data.status,
                details=ReportDetails(
                    reason=request_data.details.reason,
                    description=request_data.details.description,
                    documents=cls.create_document_objects(now, base_url, request_data.details.documents),
                    dateModified=now,
                ),
                dateCreated=now,
                dateModified=now,
            )
        )
        return create_obj

    @classmethod
    def validate_publish(
        cls,
        violation_report: ViolationReportDBModel,
    ) -> None:
        cls.validate_documents_before_publish(violation_report.details)

    @staticmethod
    def validate_update_allowed_status(violation_report: ViolationReportDBModel):
        if violation_report.status != ViolationReportStatus.draft:
            raise JsonHTTPBadRequest(details=f"Details update forbidden in '{violation_report.status}' status")

    @classmethod
    def update_details(
        cls,
        violation_report: ViolationReportDBModel,
        request_data: ViolationReportPatchDetailsRequestData,
    ) -> Optional[ViolationReportDBModel]:
        now = get_now_async()
        # if there are more fields, you could use .model_copy(update=...) and compare with result object
        if (
            violation_report.details.description != request_data.details.description
            or violation_report.details.reason != request_data.details.reason
        ):
            violation_report.details.reason = request_data.details.reason
            violation_report.details.description = request_data.details.description
            violation_report.details.dateModified = now
            return violation_report
        return None

    @classmethod
    def publish_report(cls, *, violation_report: ViolationReportDBModel, tender: Tender) -> None:
        now = get_now_async()
        violation_report.datePublished = now
        violation_report.dateModified = now
        violation_report.defendantPeriod = cls.build_defendant_period(now, tender)
        violation_report.status = ViolationReportStatus.pending

    # DOCUMENTS
    @classmethod
    def validate_post_document(cls, violation_report: ViolationReportDBModel, document: PostDocument):
        cls.validate_update_allowed_status(violation_report)

        if document.documentType == DocumentTypes.violationReportSignature and any(
            d.documentType == DocumentTypes.violationReportSignature for d in violation_report.details.documents
        ):
            raise JsonHTTPBadRequest(details="Signature document already exists. Update it with PUT method instead.")

    @classmethod
    def post_document(
        cls,
        violation_report: ViolationReportDBModel,
        base_url: str,
        document: PostDocument,
    ) -> Document:
        now = get_now_async()
        documents = cls.create_document_objects(now, base_url, [document])

        violation_report.details.documents.append(documents[0])  # allow post multiple ?
        violation_report.details.dateModified = now
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
            violation_report.details.documents[doc_index] = updated_document  # update document

            now = get_now_async()
            updated_document.dateModified = now
            violation_report.details.dateModified = now
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
        update = documents[0].model_dump(exclude={"id", "author", "documentType"})

        new_document = document.model_copy(update=update)
        violation_report.details.documents.append(new_document)

        violation_report.details.dateModified = now

        return new_document

    @classmethod
    def delete_document(
        cls,
        violation_report: ViolationReportDBModel,
        document_id: str,
    ) -> Optional[ViolationReportDBModel]:
        doc_len = len(violation_report.details.documents)
        violation_report.details.documents = [d for d in violation_report.details.documents if d.id != document_id]
        if doc_len != len(violation_report.details.documents):
            violation_report.details.dateModified = get_now_async()
            return violation_report
        return None
