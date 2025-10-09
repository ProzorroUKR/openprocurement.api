import logging
from typing import List

from aiohttp.web import HTTPNotFound
from aiohttp_pydantic.oas.typing import r200, r201

from openprocurement.api.context_async import (
    get_now_async,
    get_request_logging_context,
    get_view_url,
)
from openprocurement.api.errors_async import JsonHTTPNotFound
from openprocurement.api.handlers.base import BaseView
from openprocurement.api.models_async.common import DataModel
from openprocurement.api.models_async.document import Document, RequestDocument
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
from openprocurement.violation_report.state.defendant import (
    ViolationReportDefendantState,
)

logger = logging.getLogger(__name__)


class DefendantStatementView(BaseView):
    view_name = "violation_report_defendant_statement"

    async def get(self, violation_report_id: str, /) -> r200[DataModel[DefendantStatementDBModel]]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        if violation_report.defendantStatement is None:
            raise JsonHTTPNotFound(details="Defendant statement not found.")
        return {"data": ViolationReportDefendantStatementSerializer(violation_report.defendantStatement).data}

    async def put(
        self, violation_report_id: str, /, body: DataModel[DefendantStatementRequestData]
    ) -> r201[DataModel[DefendantStatementDBModel]]:
        violation_report = await get_violation_report_or_404(violation_report_id)

        # validate set statement
        now = get_now_async()
        ViolationReportDefendantState.validate_defendant_period(violation_report=violation_report, now=now)

        # create obj
        defendant_statement = ViolationReportDefendantState.create_defendant_statement(
            violation_report,
            data=body.data,
            now=now,
        )
        await update_violation_report(violation_report)

        logger.info(
            "Violation Report Defendant Statement is set",
            extra=get_request_logging_context({"MESSAGE_ID": "SET_VIOLATION_REPORT_DEFENDANT_STATEMENT"}),
        )
        return {"data": ViolationReportDefendantStatementSerializer(defendant_statement).data}


class DefendantStatementDocumentListView(BaseView):
    view_name = "defendant_statement_document_list"

    async def get(self, violation_report_id: str, /) -> r200[DataModel[List[Document]]]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        return {"data": [DocumentSerializer(d).data for d in violation_report.defendantStatement.documents]}

    async def post(self, violation_report_id: str, /, body: DataModel[RequestDocument]) -> r200[DataModel[Document]]:
        violation_report = await get_violation_report_or_404(violation_report_id)

        now = get_now_async()
        ViolationReportDefendantState.validate_add_document(violation_report, body.data, now=now)

        base_url = get_view_url(DefendantStatementView.view_name, violation_report_id=violation_report_id)
        document = ViolationReportDefendantState.add_document(
            violation_report,
            body.data,
            base_url=base_url,
            now=now,
        )
        await update_violation_report(violation_report)

        return {"data": DocumentSerializer(document).data}


class DefendantStatementDocumentView(BaseView):
    view_name = "defendant_statement_document"

    async def get(self, violation_report_id: str, document_id: str, /) -> r200[DataModel[Document]]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        if violation_report.defendantStatement is None:
            raise JsonHTTPNotFound(details="Defendant statement not found.")

        for document in violation_report.defendantStatement.documents:
            if document.id == document_id:
                if download := self.request.query.get("download"):
                    if download not in document.url:
                        raise JsonHTTPNotFound(details="Download not found.")
                    return download_file(
                        document=document,
                        config=self.request.app.doc_storage_config,
                        doc_id=download,
                    )
                return {"data": DocumentSerializer(document).data}

        raise HTTPNotFound(text="Document not found.")
