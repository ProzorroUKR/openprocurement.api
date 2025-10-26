import logging
from typing import List, Tuple

from aiohttp.web import HTTPNotFound
from aiohttp_pydantic.oas.typing import r200, r201

from prozorro_cdb.api.context import get_request_logging_context, get_view_url
from prozorro_cdb.api.database.schema.document import Document
from prozorro_cdb.api.errors import JsonHTTPNotFound
from prozorro_cdb.api.handlers.base import BaseView
from prozorro_cdb.api.handlers.schema.common import DataModel
from prozorro_cdb.api.handlers.schema.document import GetDocumentResponse
from prozorro_cdb.api.serializers.document import DocumentSerializer
from prozorro_cdb.api.storage import download_file
from prozorro_cdb.violation_report.database.helpers import (
    get_violation_report_or_404,
    update_violation_report,
)
from prozorro_cdb.violation_report.database.schema.violation_report import (
    DefendantStatementDBModel,
    ViolationReportDBModel,
)
from prozorro_cdb.violation_report.handlers.schema.defendant_statement import (
    DefendantStatementRequestData,
)
from prozorro_cdb.violation_report.handlers.schema.document import (
    PatchDocument,
    PostDocument,
)
from prozorro_cdb.violation_report.serializers.defendant_statement import (
    ViolationReportDefendantStatementSerializer,
)
from prozorro_cdb.violation_report.state.defendant import ViolationReportDefendantState

logger = logging.getLogger(__name__)


class DefendantStatementView(BaseView):
    view_name = "violation_report_defendant_statement"

    async def get(self, violation_report_id: str, /) -> r200[DataModel[DefendantStatementDBModel]]:
        """
        Tags: ViolationReports.defendantStatement
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        if violation_report.defendantStatement is None:
            raise JsonHTTPNotFound(details="Defendant statement not found.")
        return {"data": ViolationReportDefendantStatementSerializer(violation_report.defendantStatement).data}

    async def put(
        self, violation_report_id: str, /, body: DataModel[DefendantStatementRequestData]
    ) -> r201[DataModel[DefendantStatementDBModel]]:
        """
        Tags: ViolationReports.defendantStatement
        """
        violation_report = await get_violation_report_or_404(violation_report_id)

        # validate set statement
        ViolationReportDefendantState.validate_defendant_period(violation_report=violation_report)

        # create obj
        defendant_statement = ViolationReportDefendantState.create_defendant_statement(
            violation_report,
            data=body.data,
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
        """
        Tags: ViolationReports.defendantStatement
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        return {"data": [DocumentSerializer(d).data for d in violation_report.defendantStatement.documents]}

    async def post(self, violation_report_id: str, /, body: DataModel[PostDocument]) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.defendantStatement
        """
        violation_report = await get_violation_report_or_404(violation_report_id)

        ViolationReportDefendantState.validate_post_document(violation_report, body.data)

        base_url = get_view_url(DefendantStatementView.view_name, violation_report_id=violation_report_id)
        document = ViolationReportDefendantState.post_document(
            violation_report,
            body.data,
            base_url=base_url,
        )
        await update_violation_report(violation_report)
        logger.info(
            "Violation Report defendant document post",
            extra=get_request_logging_context({"MESSAGE_ID": "POST_VIOLATION_REPORT_DEFENDANT_DOCUMENT"}),
        )

        return {"data": DocumentSerializer(document).data}


class DefendantStatementDocumentView(BaseView):
    view_name = "defendant_statement_document"

    @staticmethod
    async def resolve_document(
        violation_report_id: str, document_id: str
    ) -> Tuple[Document, int, ViolationReportDBModel]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        for doc_index, document in enumerate(reversed(violation_report.defendantStatement.documents)):
            if document.id == document_id:
                return document, doc_index, violation_report
        else:
            raise HTTPNotFound(text="Document not found.")

    async def get(self, violation_report_id: str, document_id: str, /) -> r200[DataModel[GetDocumentResponse]]:
        """
        Tags: ViolationReports.defendantStatement
        """
        document, _, violation_report = await self.resolve_document(violation_report_id, document_id)

        if download := self.request.query.get("download"):
            if download not in document.url:
                raise JsonHTTPNotFound(details="Download not found.")
            return download_file(document=document, doc_id=download)

        document_data = document.model_dump(exclude_none=True)
        document_data["previousVersions"] = [
            DocumentSerializer(i).data
            for i in violation_report.defendantStatement.documents
            if i.id == document.id and i.url != document.url
        ]
        return {"data": DocumentSerializer(document_data).data}

    async def patch(
        self, violation_report_id: str, document_id: str, /, body: DataModel[PatchDocument]
    ) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.defendantStatement
        """
        document, doc_index, violation_report = await self.resolve_document(violation_report_id, document_id)

        ViolationReportDefendantState.validate_defendant_period(violation_report=violation_report)
        new_document = ViolationReportDefendantState.patch_document(
            violation_report,
            document=document,
            doc_index=doc_index,
            updates=body.data,
        )
        if new_document:
            await update_violation_report(violation_report)
            logger.info(
                "Violation report document patch",
                extra=get_request_logging_context({"MESSAGE_ID": "PATCH_VIOLATION_REPORT_DEFENDANT_DOCUMENT"}),
            )
            return {"data": DocumentSerializer(new_document).data}

        return {"data": DocumentSerializer(document).data}

    async def put(
        self, violation_report_id: str, document_id: str, /, body: DataModel[PostDocument]
    ) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.defendantStatement
        """
        document, doc_index, violation_report = await self.resolve_document(violation_report_id, document_id)

        ViolationReportDefendantState.validate_defendant_period(violation_report=violation_report)

        base_url = get_view_url(DefendantStatementView.view_name, violation_report_id=violation_report_id)
        new_document = ViolationReportDefendantState.put_document(
            violation_report,
            base_url=base_url,
            document_data=body.data,
            document=document,
        )

        await update_violation_report(violation_report)
        logger.info(
            "Violation report document put",
            extra=get_request_logging_context({"MESSAGE_ID": "PUT_VIOLATION_REPORT_DEFENDANT_DOCUMENT"}),
        )
        return {"data": DocumentSerializer(new_document).data}
