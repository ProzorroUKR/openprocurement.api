from aiohttp.web import HTTPBadRequest

from openprocurement.api.context_async import get_now_async
from openprocurement.api.errors_async import JsonHTTPBadRequest
from openprocurement.api.models_async.document import DocumentTypes
from openprocurement.api.storage_async import upload_documents
from openprocurement.violation_report.database.schema.violation_report import (
    Document,
    ViolationReportDBModel,
    ViolationReportDecisionDBModel,
)
from openprocurement.violation_report.handlers.schema.decision import (
    DecisionRequestData,
)


class ViolationReportDecisionState:
    def __init__(
        self,
        data: DecisionRequestData,
        violation_report: ViolationReportDBModel,
    ) -> None:
        self.violation_report = violation_report
        self.request_data = data

        # overwrite is forbidden
        if self.violation_report.decision is not None:
            raise JsonHTTPBadRequest(
                message="decision already created.",
            )

        # validate period
        now = get_now_async()
        period = self.violation_report.decisionPeriod
        if not (period.startDate < now <= period.endDate):
            raise JsonHTTPBadRequest(
                message="Can add decision only during decisionPeriod.",
                now=now,
                period=period.model_dump(mode="json"),
            )

        # validate signature document provided
        document_types = {d.documentType for d in data.documents}
        if DocumentTypes.violationReportSignature not in document_types:
            raise HTTPBadRequest(text="Signature document not found.")

    def create_decision(self, base_url: str) -> ViolationReportDecisionDBModel:
        request_data = self.request_data
        now = get_now_async()

        create_obj = ViolationReportDecisionDBModel(
            status=request_data.status,
            description=request_data.description,
            documents=[
                Document(id=document_id, datePublished=now, dateModified=now, **d.model_dump())
                for document_id, d in upload_documents(
                    current_url=base_url,
                    documents=request_data.documents,
                )
            ],
            dateCreated=now,
        )
        return create_obj
