import logging

from aiohttp.web import HTTPNotFound
from aiohttp_pydantic.oas.typing import r200, r201

from openprocurement.api.context_async import get_request_logging_context, get_view_url
from openprocurement.api.errors_async import JsonHTTPNotFound
from openprocurement.api.handlers.base import BaseView
from openprocurement.api.models_async.common import DataModel
from openprocurement.api.models_async.document import Document
from openprocurement.api.serializers_async.document import DocumentSerializer
from openprocurement.api.storage_async import download_file
from openprocurement.violation_report.database.helpers import (
    get_violation_report_or_404,
    update_violation_report,
)
from openprocurement.violation_report.database.schema.violation_report import (
    DefendantStatementDBModel,
)
from openprocurement.violation_report.handlers.schema.defendant_statement import (
    DefendantStatementRequestData,
)
from openprocurement.violation_report.serializers.defendant_statement import (
    ViolationReportDefendantStatementSerializer,
)
from openprocurement.violation_report.state.pending import ViolationReportPendingState

logger = logging.getLogger(__name__)


class DefendantStatementView(BaseView):
    view_name = "violation_report_defendant_statement"

    async def get(self, violation_report_id: str, /) -> r200[DataModel[DefendantStatementDBModel]]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        if violation_report.defendantStatement is None:
            raise JsonHTTPNotFound(message="Defendant statement not found.")
        return {"data": ViolationReportDefendantStatementSerializer(violation_report.defendantStatement).data}

    async def put(
        self, violation_report_id: str, /, body: DataModel[DefendantStatementRequestData]
    ) -> r201[DataModel[DefendantStatementDBModel]]:
        violation_report = await get_violation_report_or_404(violation_report_id)

        # create state and validate input
        state = ViolationReportPendingState(violation_report=violation_report, data=body.data)

        # create obj
        base_url = get_view_url(self.view_name, violation_report_id=violation_report_id)
        violation_report.defendantStatement = state.create_defendant_statement(base_url=str(base_url))

        # save it to the db
        violation_report = await update_violation_report(violation_report)

        logger.info(
            "Violation Report Defendant Statement created",
            extra=get_request_logging_context({"MESSAGE_ID": "CREATE_VIOLATION_REPORT_DEFENDANT_STATEMENT"}),
        )
        return {"data": ViolationReportDefendantStatementSerializer(violation_report.defendantStatement).data}


class DefendantStatementDocumentView(BaseView):
    view_name = "defendant_statement_document"

    async def get(self, violation_report_id: str, document_id: str, /) -> r200[DataModel[Document]]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        if violation_report.defendantStatement is None:
            raise JsonHTTPNotFound(message="Defendant statement not found.")

        for document in violation_report.defendantStatement.documents:
            if document.id == document_id:
                if download := self.request.query.get("download"):
                    if download not in document.url:
                        raise JsonHTTPNotFound(message="Download not found.")
                    return download_file(
                        document=document,
                        config=self.request.app.doc_storage_config,
                        doc_id=download,
                    )
                return {"data": DocumentSerializer(document).data}

        raise HTTPNotFound(text="Document not found.")
