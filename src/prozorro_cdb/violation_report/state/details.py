from typing import Optional

from aiohttp.web import HTTPBadRequest

from openprocurement.api.constants import SANDBOX_MODE
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
    ViolationReportReason,
    ViolationReportStatus,
)
from prozorro_cdb.violation_report.handlers.schema.document import PatchDocument
from prozorro_cdb.violation_report.handlers.schema.violation_report import (
    ReportDetailsRequestData,
    ViolationReportPatchRequestData,
    ViolationReportPostRequestData,
)


class ViolationReportDetailsState(BaseState):
    @classmethod
    def validate_create(
        cls,
        request_data: ViolationReportPostRequestData,
        contract: Contract,
    ) -> None:
        # validate the reason is reasonable
        details = request_data.details
        if (
            details.reason in (ViolationReportReason.goodsNonCompliance, ViolationReportReason.contractBreach)
            and not contract.dateSigned
        ):
            raise HTTPBadRequest(text="Contract is not signed.")
        elif details.reason == ViolationReportReason.signingRefusal and contract.dateSigned:
            raise HTTPBadRequest(text="Contract is signed.")

        signatures = [d for d in details.documents if d.documentType == DocumentTypes.violationReportSignature]
        if len(signatures) > 1:
            raise HTTPBadRequest(text="More than one signature document found.")

        if request_data.status == ViolationReportStatus.pending:
            cls.validate_documents_before_publish(details)

    @staticmethod
    def validate_documents_before_publish(details: ReportDetailsRequestData | ReportDetails):
        # validate both evidence and signature documents provided
        documents = {d.documentType: d for d in details.documents}
        if DocumentTypes.violationReportSignature not in documents:
            raise HTTPBadRequest(text="Signature document not found.")
        if DocumentTypes.violationReportEvidence not in documents:
            raise HTTPBadRequest(text="Evidence document not found.")
        signature = documents[DocumentTypes.violationReportSignature]

        if signature.dateModified < details.dateModified:
            raise HTTPBadRequest(text="Signature document should be uploaded after any detail changes.")

    @staticmethod
    def build_defendant_period(published_date, tender: Tender) -> Period:
        # to test real periods with accelerated tenders
        tender_dict = (tender.model_dump() if SANDBOX_MODE else {},)
        defendant_period_end = calculate_tender_full_date(
            date_obj=published_date,
            timedelta_obj=DEFENDANT_PERIOD_TD,
            working_days=True,
            tender=tender_dict,
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

        if request_data.status == ViolationReportStatus.pending:
            cls.publish_report(create_obj, tender)

        return create_obj

    @classmethod
    def validate_update(
        cls,
        violation_report: ViolationReportDBModel,
        request_data: ViolationReportPatchRequestData,
    ) -> None:
        cls.validate_update_allowed_status(violation_report)

        if request_data.status is not None and request_data.status == ViolationReportStatus.pending:
            cls.validate_documents_before_publish(violation_report.details)

    @staticmethod
    def validate_update_allowed_status(violation_report: ViolationReportDBModel):
        if violation_report.status != ViolationReportStatus.draft:
            raise JsonHTTPBadRequest(details=f"Details update forbidden in '{violation_report.status}' status")

    @classmethod
    def update_object(
        cls,
        tender: Tender,
        violation_report: ViolationReportDBModel,
        request_data: ViolationReportPatchRequestData,
    ) -> Optional[ViolationReportDBModel]:
        now = get_now_async()
        updates_found = False

        # if there are more fields, you could use .model_copy(update=...) and compare with result object
        if (
            request_data.details is not None
            and violation_report.details.description != request_data.details.description
        ):
            violation_report.details.description = request_data.details.description
            violation_report.details.dateModified = now

            updates_found = True

        if (
            request_data.status is not None
            and violation_report.status == ViolationReportStatus.draft
            and request_data.status == ViolationReportStatus.pending
        ):
            cls.publish_report(violation_report, tender)
            updates_found = True

        if updates_found:
            violation_report.dateModified = now
            return violation_report
        return None

    @classmethod
    def publish_report(cls, violation_report: ViolationReportDBModel, tender: Tender) -> None:
        now = get_now_async()
        violation_report.datePublished = now
        violation_report.defendantPeriod = cls.build_defendant_period(now, tender)
        violation_report.status = ViolationReportStatus.pending

    # DOCUMENTS
    @classmethod
    def validate_post_document(cls, violation_report: ViolationReportDBModel, document: PostDocument):
        cls.validate_update_allowed_status(violation_report)

        if document.documentType == DocumentTypes.violationReportSignature and any(
            d.documentType == DocumentTypes.violationReportSignature for d in violation_report.details.documents
        ):
            raise HTTPBadRequest(text="Signature document already exists. Update it with PUT method instead.")

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
        update = documents[0].model_dump(exclude={"id", "author", "format", "documentType"})

        new_document = document.model_copy(update=update)
        violation_report.details.documents.append(new_document)

        violation_report.details.dateModified = now
        violation_report.dateModified = now

        return new_document
