from datetime import timedelta

from aiohttp.web import HTTPBadRequest

from openprocurement.api.context_async import get_now_async
from openprocurement.api.models_async.common import Period
from openprocurement.api.models_async.document import DocumentTypes
from openprocurement.api.storage_async import upload_documents
from openprocurement.api.utils import calculate_date, calculate_normalized_date
from openprocurement.violation_report.constants import (
    DECISION_PERIOD_TD,
    DEFENDANT_PERIOD_TD,
)
from openprocurement.violation_report.database.schema.contract import Contract
from openprocurement.violation_report.database.schema.violation_report import (
    Document,
    ViolationReportDBModel,
    ViolationReportReason,
)
from openprocurement.violation_report.handlers.schema.violation_report import (
    ViolationReportDraftRequestData,
)


class ViolationReportDraftState:
    def __init__(self, data: ViolationReportDraftRequestData, contract: Contract) -> None:
        self.contract = contract
        self.request_data = data

        # validate the reason is reasonable
        if (
            data.reason in (ViolationReportReason.goodsNonCompliance, ViolationReportReason.contractBreach)
            and not contract.dateSigned
        ):
            raise HTTPBadRequest(text="Contract is not signed.")
        elif data.reason == ViolationReportReason.signingRefusal and contract.dateSigned:
            raise HTTPBadRequest(text="Contract is signed.")

        # validate both evidence and signature documents provided
        document_types = {d.documentType for d in data.documents}
        if DocumentTypes.violationReportSignature not in document_types:
            raise HTTPBadRequest(text="Signature document not found.")
        if DocumentTypes.violationReportEvidence not in document_types:
            raise HTTPBadRequest(text="Evidence document not found.")

    def create_from_user_input(self, uid: str, base_url: str) -> ViolationReportDBModel:
        contract = self.contract
        request_data = self.request_data
        now = get_now_async()

        defendant_period_start = calculate_normalized_date(now, ceil=True)
        defendant_period_end = calculate_date(
            defendant_period_start, timedelta_obj=DEFENDANT_PERIOD_TD, working_days=True
        )
        decision_period_start = calculate_date(defendant_period_end, timedelta_obj=timedelta(days=1), working_days=True)
        create_obj = ViolationReportDBModel.model_validate(
            dict(
                _id=uid,
                contract_id=contract.id,
                tender_id=contract.tender_id,
                dateCreated=now,
                dateModified=now,
                reason=request_data.reason,
                description=request_data.description,
                documents=[
                    Document.model_validate(dict(id=document_id, datePublished=now, dateModified=now, **d.model_dump()))
                    for document_id, d in upload_documents(
                        current_url=base_url,
                        documents=request_data.documents,
                    )
                ],
                buyer=contract.buyer,
                suppliers=contract.suppliers,
                # frameworks.procuringEntity,
                defendantPeriod=Period(
                    startDate=now,
                    endDate=defendant_period_end,
                ),
                decisionPeriod=Period(
                    startDate=decision_period_start,
                    endDate=calculate_date(decision_period_start, timedelta_obj=DECISION_PERIOD_TD, working_days=True),
                ),
            )
        )
        return create_obj
