import logging
from typing import List, Optional, Tuple, Union
from uuid import uuid4

from aiohttp.web import HTTPNoContent, HTTPNotFound
from aiohttp_pydantic.oas.typing import r200, r201, r204

from prozorro_cdb.api.context import (
    get_request_logging_context,
    get_view_url,
    url_to_absolute,
)
from prozorro_cdb.api.database.schema.document import Document
from prozorro_cdb.api.errors import JsonHTTPNotFound
from prozorro_cdb.api.handlers.base import BaseView
from prozorro_cdb.api.handlers.schema.common import DataModel
from prozorro_cdb.api.handlers.schema.document import GetDocumentResponse
from prozorro_cdb.api.middlewares import json_response
from prozorro_cdb.api.serializers.document import DocumentSerializer
from prozorro_cdb.api.storage import download_file
from prozorro_cdb.violation_report.database.helpers import (
    get_violation_report_or_404,
    update_violation_report,
)
from prozorro_cdb.violation_report.database.schema.violation_report import (
    DefendantStatementDBModel,
    DraftActiveObjectStatus,
    ViolationReportDBModel,
)
from prozorro_cdb.violation_report.handlers.schema.defendant_statement import (
    DefendantStatementActivateRequestData,
    DefendantStatementPatchRequestData,
    DefendantStatementPostRequestData,
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


class DefendantStatementListView(BaseView):
    view_name = "violation_report_defendant_statement_list"

    async def get(self, violation_report_id: str, /) -> r200[DataModel[list[DefendantStatementDBModel]]]:
        """
        Tags: ViolationReports.defendantStatements
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        return {
            "data": [
                ViolationReportDefendantStatementSerializer(obj).data
                for obj in violation_report.defendantStatements
                if obj.status != DraftActiveObjectStatus.draft
            ]
        }

    async def post(
        self, violation_report_id: str, /, body: DataModel[DefendantStatementPostRequestData]
    ) -> r201[DataModel[DefendantStatementDBModel]]:
        """
        Tags: ViolationReports.defendantStatements
        """
        violation_report = await get_violation_report_or_404(violation_report_id)

        # validate create statement
        ViolationReportDefendantState.validate_create(violation_report=violation_report)

        # create obj
        defendant_statement_id = uuid4().hex
        base_url = get_view_url(
            DefendantStatementView.view_name,
            violation_report_id=violation_report_id,
            defendant_statement_id=defendant_statement_id,
        )
        defendant_statement = ViolationReportDefendantState.create_defendant_statement(
            uid=defendant_statement_id,
            base_url=base_url,
            violation_report=violation_report,
            data=body.data,
        )
        await update_violation_report(violation_report, modified=False)

        logger.info(
            "Violation Report Defendant Statement posted",
            extra=get_request_logging_context({"MESSAGE_ID": "POST_VIOLATION_REPORT_DEFENDANT_STATEMENT"}),
        )
        return json_response(
            status=201,
            data={"data": ViolationReportDefendantStatementSerializer(defendant_statement).data},
            headers={"Location": url_to_absolute(base_url)},
        )


class DefendantStatementDetailMixing:
    @staticmethod
    def get_defendant_statement(
        violation_report: ViolationReportDBModel, defendant_statement_id: str
    ) -> DefendantStatementDBModel:
        for defendant_statement in violation_report.defendantStatements:
            if defendant_statement.id == defendant_statement_id:
                return defendant_statement
        else:
            raise JsonHTTPNotFound(details="defendantStatement not found.")


class DefendantStatementView(DefendantStatementDetailMixing, BaseView):
    view_name = "violation_report_defendant_statement"

    async def get(
        self, violation_report_id: str, defendant_statement_id: str, /
    ) -> r200[DataModel[DefendantStatementDBModel]]:
        """
        Tags: ViolationReports.defendantStatements
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        obj = self.get_defendant_statement(violation_report, defendant_statement_id)
        return {"data": ViolationReportDefendantStatementSerializer(obj).data}

    async def patch(
        self,
        violation_report_id: str,
        defendant_statement_id: str,
        /,
        body: DataModel[Union[DefendantStatementPatchRequestData, DefendantStatementActivateRequestData]],
    ) -> r201[DataModel[DefendantStatementDBModel]]:
        """
        Tags: ViolationReports.defendantStatements
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        defendant_statement = self.get_defendant_statement(violation_report, defendant_statement_id)
        if (
            isinstance(body.data, DefendantStatementActivateRequestData)
            and defendant_statement.status != DraftActiveObjectStatus.active
        ):
            ViolationReportDefendantState.validate_publish_defendant_statement(
                violation_report,
                defendant_statement,
            )
            ViolationReportDefendantState.publish_defendant_statement(
                violation_report=violation_report,
                defendant_statement=defendant_statement,
            )
            await update_violation_report(violation_report, modified=True)
            logger.info(
                "Violation Report Defendant Statement updated",
                extra=get_request_logging_context({"MESSAGE_ID": "VIOLATION_REPORT_DEFENDANT_STATEMENT_ACTIVATED"}),
            )
        elif isinstance(body.data, DefendantStatementPatchRequestData):
            ViolationReportDefendantState.validate_update_defendant_statement(
                violation_report,
                defendant_statement,
            )
            updated_defendant_statement = ViolationReportDefendantState.update_defendant_statement(
                defendant_statement=defendant_statement,
                data=body.data,
            )
            if updated_defendant_statement:
                await update_violation_report(violation_report, modified=False)
            logger.info(
                "Violation Report Defendant Statement updated",
                extra=get_request_logging_context({"MESSAGE_ID": "VIOLATION_REPORT_DEFENDANT_STATEMENT_UPDATED"}),
            )
        return {"data": ViolationReportDefendantStatementSerializer(defendant_statement).data}


class DefendantStatementDocumentListView(DefendantStatementDetailMixing, BaseView):
    view_name = "defendant_statement_document_list"

    async def get(self, violation_report_id: str, defendant_statement_id: str, /) -> r200[DataModel[List[Document]]]:
        """
        Tags: ViolationReports.defendantStatements
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        obj = self.get_defendant_statement(violation_report, defendant_statement_id)
        return {"data": [DocumentSerializer(d).data for d in obj.documents]}

    async def post(
        self, violation_report_id: str, defendant_statement_id: str, /, body: DataModel[PostDocument]
    ) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.defendantStatements
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        defendant_statement = self.get_defendant_statement(violation_report, defendant_statement_id)

        ViolationReportDefendantState.validate_post_document(violation_report, defendant_statement, body.data)

        base_url = get_view_url(
            DefendantStatementView.view_name,
            violation_report_id=violation_report_id,
            defendant_statement_id=defendant_statement_id,
        )
        document = ViolationReportDefendantState.post_document(
            defendant_statement,
            body.data,
            base_url=base_url,
        )
        await update_violation_report(violation_report, modified=False)
        logger.info(
            "Violation Report defendant document post",
            extra=get_request_logging_context({"MESSAGE_ID": "POST_VIOLATION_REPORT_DEFENDANT_DOCUMENT"}),
        )
        return {"data": DocumentSerializer(document).data}


class DefendantStatementDocumentView(DefendantStatementDetailMixing, BaseView):
    view_name = "defendant_statement_document"

    async def resolve_document(
        self,
        violation_report_id: str,
        defendant_statement_id: str,
        document_id: str,
        download: Optional[str] = None,
    ) -> Tuple[Document, int, DefendantStatementDBModel, ViolationReportDBModel]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        obj = self.get_defendant_statement(violation_report, defendant_statement_id)
        for doc_index, document in reversed(list(enumerate(obj.documents))):
            if document.id == document_id and (download is None or download in document.url):
                return document, doc_index, obj, violation_report
        else:
            raise HTTPNotFound(text="Document not found.")

    async def get(
        self, violation_report_id: str, defendant_statement_id: str, document_id: str, /
    ) -> r200[DataModel[GetDocumentResponse]]:
        """
        Tags: ViolationReports.defendantStatements
        """
        document, _, defendant_statement, _ = await self.resolve_document(
            violation_report_id,
            defendant_statement_id,
            document_id,
            download=self.request.query.get("download"),
        )
        if download := self.request.query.get("download"):
            return download_file(document=document, doc_id=download)

        document_data = document.model_dump(exclude_none=True)
        document_data["previousVersions"] = [
            DocumentSerializer(i).data
            for i in defendant_statement.documents
            if i.id == document.id and i.url != document.url
        ]
        return {"data": DocumentSerializer(document_data).data}

    async def patch(
        self, violation_report_id: str, defendant_statement_id: str, document_id: str, /, body: DataModel[PatchDocument]
    ) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.defendantStatements
        """
        document, doc_index, defendant_statement, violation_report = await self.resolve_document(
            violation_report_id, defendant_statement_id, document_id
        )

        ViolationReportDefendantState.validate_update_defendant_statement(violation_report, defendant_statement)

        new_document = ViolationReportDefendantState.patch_document(
            defendant_statement=defendant_statement,
            document=document,
            doc_index=doc_index,
            updates=body.data,
        )
        if new_document:
            await update_violation_report(violation_report, modified=False)
            logger.info(
                "Violation report defendant document patch",
                extra=get_request_logging_context({"MESSAGE_ID": "PATCH_VIOLATION_REPORT_DEFENDANT_DOCUMENT"}),
            )
            return {"data": DocumentSerializer(new_document).data}

        return {"data": DocumentSerializer(document).data}

    async def put(
        self, violation_report_id: str, defendant_statement_id: str, document_id: str, /, body: DataModel[PostDocument]
    ) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.defendantStatements
        """
        document, doc_index, defendant_statement, violation_report = await self.resolve_document(
            violation_report_id, defendant_statement_id, document_id
        )

        ViolationReportDefendantState.validate_update_defendant_statement(violation_report, defendant_statement)

        base_url = get_view_url(
            DefendantStatementView.view_name,
            violation_report_id=violation_report_id,
            defendant_statement_id=defendant_statement_id,
        )
        new_document = ViolationReportDefendantState.put_document(
            defendant_statement=defendant_statement,
            base_url=base_url,
            document_data=body.data,
            document=document,
        )
        await update_violation_report(violation_report, modified=False)
        logger.info(
            "Violation report defendant document put",
            extra=get_request_logging_context({"MESSAGE_ID": "PUT_VIOLATION_REPORT_DEFENDANT_DOCUMENT"}),
        )
        return {"data": DocumentSerializer(new_document).data}

    async def delete(self, violation_report_id: str, defendant_statement_id: str, document_id: str, /) -> r204[None]:
        """
        Tags: ViolationReports.defendantStatements
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        defendant_statement = self.get_defendant_statement(violation_report, defendant_statement_id)

        ViolationReportDefendantState.validate_update_defendant_statement(violation_report, defendant_statement)

        updated = ViolationReportDefendantState.delete_document(defendant_statement, document_id=document_id)
        if updated:
            await update_violation_report(violation_report)
            logger.info(
                "Violation report defendant document delete",
                extra=get_request_logging_context({"MESSAGE_ID": "DELETE_VIOLATION_REPORT_DEFENDANT_DOCUMENT"}),
            )
        return HTTPNoContent()
