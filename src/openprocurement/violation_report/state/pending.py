from aiohttp.web import HTTPBadRequest

from openprocurement.api.context_async import get_now_async
from openprocurement.api.errors_async import JsonHTTPBadRequest
from openprocurement.api.models_async.document import DocumentTypes
from openprocurement.api.storage_async import upload_documents
from openprocurement.violation_report.database.schema.violation_report import (
    DefendantStatementDBModel,
    Document,
    ViolationReportDBModel,
)
from openprocurement.violation_report.handlers.schema.defendant_statement import (
    DefendantStatementRequestData,
)


class ViolationReportPendingState:
    def __init__(
        self,
        data: DefendantStatementRequestData,
        violation_report: ViolationReportDBModel,
    ) -> None:
        self.violation_report = violation_report
        self.request_data = data

        # overwrite is forbidden
        if self.violation_report.defendantStatement is not None:
            raise JsonHTTPBadRequest(
                message="defendantStatement already created.",
            )

        # validate period
        now = get_now_async()
        period = self.violation_report.defendantPeriod
        if not (period.startDate < now <= period.endDate):
            raise JsonHTTPBadRequest(
                message="Can add defendantStatement only during defendantPeriod.",
                now=now,
                period=period.model_dump(mode="json"),
            )

        # validate both evidence and signature documents provided
        document_types = {d.documentType for d in data.documents}
        if DocumentTypes.violationReportSignature not in document_types:
            raise HTTPBadRequest(text="Signature document not found.")
        if DocumentTypes.violationReportEvidence not in document_types:
            raise HTTPBadRequest(text="Evidence document not found.")

    def create_defendant_statement(self, base_url: str) -> DefendantStatementDBModel:
        request_data = self.request_data
        now = get_now_async()

        create_obj = DefendantStatementDBModel(
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
