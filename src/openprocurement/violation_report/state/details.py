from typing import Optional

from aiohttp.web import HTTPBadRequest

from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.context_async import get_now_async
from openprocurement.api.errors_async import JsonHTTPBadRequest
from openprocurement.api.models_async.common import Period
from openprocurement.api.models_async.document import DocumentTypes, RequestDocument
from openprocurement.tender.core.utils import calculate_tender_full_date
from openprocurement.violation_report.constants import DEFENDANT_PERIOD_TD
from openprocurement.violation_report.database.schema.agreement import Agreement
from openprocurement.violation_report.database.schema.contract import Contract
from openprocurement.violation_report.database.schema.tender import Tender
from openprocurement.violation_report.database.schema.violation_report import (
    Document,
    ReportDetails,
    ViolationReportDBModel,
    ViolationReportReason,
    ViolationReportStatus,
)
from openprocurement.violation_report.handlers.schema.violation_report import (
    ReportDetailsRequestData,
    ViolationReportPatchRequestData,
    ViolationReportPostRequestData,
)
from openprocurement.violation_report.state.base import BaseState


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
        if len(signatures):
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

        defendant_period = None
        if request_data.status == ViolationReportStatus.pending:
            defendant_period = cls.build_defendant_period(now, tender)

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
                defendantPeriod=defendant_period,
            )
        )
        return create_obj

    @classmethod
    def validate_add_details_document(cls, violation_report: ViolationReportDBModel, document: RequestDocument):
        if document.documentType == DocumentTypes.violationReportSignature and any(
            d.documentType == DocumentTypes.violationReportSignature for d in violation_report.details.documents
        ):
            raise HTTPBadRequest(text="Signature document already exists. Update it with PUT method instead.")

    @classmethod
    def add_details_document(
        cls,
        violation_report: ViolationReportDBModel,
        base_url: str,
        document: RequestDocument,
    ) -> Document:
        now = get_now_async()
        documents = cls.create_document_objects(now, base_url, [document])

        violation_report.details.documents.append(documents[0])  # allow post multiple ?
        violation_report.details.dateModified = now
        violation_report.dateModified = now
        return documents[0]

    @classmethod
    def validate_update(
        cls,
        violation_report: ViolationReportDBModel,
        request_data: ViolationReportPatchRequestData,
    ) -> None:
        if violation_report.status != ViolationReportStatus.draft:
            raise JsonHTTPBadRequest(details=f"Details update forbidden in '{violation_report.status}' status")

        if request_data.status is not None and request_data.status == ViolationReportStatus.pending:
            cls.validate_documents_before_publish(violation_report.details)

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
            violation_report.defendantPeriod = cls.build_defendant_period(now, tender)
            violation_report.status = request_data.status

            updates_found = True

        if updates_found:
            violation_report.dateModified = now
            return violation_report
        return None
