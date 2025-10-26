import logging
from typing import List, Tuple

from aiohttp.web import HTTPNotFound
from aiohttp_pydantic.oas.typing import r200, r201

from prozorro_cdb.api.context import get_request_logging_context, get_view_url
from prozorro_cdb.api.database.schema.document import Document
from prozorro_cdb.api.errors import JsonHTTPNotFound
from prozorro_cdb.api.handlers.base import BaseView
from prozorro_cdb.api.handlers.schema.common import DataModel
from prozorro_cdb.api.serializers.document import DocumentSerializer
from prozorro_cdb.api.storage import download_file
from prozorro_cdb.violation_report.database.helpers import (
    get_violation_report_or_404,
    update_violation_report,
)
from prozorro_cdb.violation_report.database.schema.violation_report import (
    ViolationReportDBModel,
    ViolationReportDecisionDBModel,
)
from prozorro_cdb.violation_report.handlers.schema.decision import DecisionRequestData
from prozorro_cdb.violation_report.handlers.schema.document import (
    PatchDocument,
    PostDocument,
)
from prozorro_cdb.violation_report.serializers.decision import (
    ViolationReportDecisionSerializer,
)
from prozorro_cdb.violation_report.state.decision import ViolationReportDecisionState

logger = logging.getLogger(__name__)


class ViolationReportDecisionView(BaseView):
    view_name = "violation_report_decision"

    async def get(self, violation_report_id: str, /) -> r200[DataModel[ViolationReportDecisionDBModel]]:
        """
        Tags: ViolationReports.decision
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        if violation_report.decision is None:
            raise HTTPNotFound(text="Decision not found.")
        return {"data": ViolationReportDecisionSerializer(violation_report.decision).data}

    async def put(
        self, violation_report_id: str, /, body: DataModel[DecisionRequestData]
    ) -> r201[DataModel[ViolationReportDecisionDBModel]]:
        """
        Tags: ViolationReports.decision
        """
        violation_report = await get_violation_report_or_404(violation_report_id)

        # create state and validate input
        ViolationReportDecisionState.validate_decision_period(violation_report=violation_report)

        # create obj
        decision = ViolationReportDecisionState.create_decision(
            violation_report=violation_report,
            data=body.data,
        )
        await update_violation_report(violation_report)

        logger.info(
            "Violation Report Decision created",
            extra=get_request_logging_context({"MESSAGE_ID": "CREATE_VIOLATION_REPORT_DECISION"}),
        )
        return {"data": ViolationReportDecisionSerializer(decision).data}


class ViolationReportDecisionDocumentListView(BaseView):
    view_name = "violation_report_decision_list"

    async def get(self, violation_report_id: str, /) -> r200[DataModel[List[Document]]]:
        """
        Tags: ViolationReports.decision
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        return {"data": [DocumentSerializer(d).data for d in violation_report.defendantStatement.documents]}

    async def post(self, violation_report_id: str, /, body: DataModel[PostDocument]) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.decision
        """
        violation_report = await get_violation_report_or_404(violation_report_id)

        ViolationReportDecisionState.validate_post_document(violation_report, body.data)

        base_url = get_view_url(ViolationReportDecisionView.view_name, violation_report_id=violation_report_id)
        document = ViolationReportDecisionState.post_document(
            violation_report,
            body.data,
            base_url=base_url,
        )
        await update_violation_report(violation_report)
        logger.info(
            "Violation Report decision document post",
            extra=get_request_logging_context({"MESSAGE_ID": "POST_VIOLATION_REPORT_DECISION_DOCUMENT"}),
        )

        return {"data": DocumentSerializer(document).data}


class ViolationReportDecisionDocumentView(BaseView):
    view_name = "violation_report_decision_document"

    @staticmethod
    async def resolve_document(
        violation_report_id: str, document_id: str
    ) -> Tuple[Document, int, ViolationReportDBModel]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        for doc_index, document in enumerate(reversed(violation_report.decision.documents)):
            if document.id == document_id:
                return document, doc_index, violation_report
        else:
            raise HTTPNotFound(text="Document not found.")

    async def get(self, violation_report_id: str, document_id: str, /) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.decision
        """
        document, _, violation_report = await self.resolve_document(violation_report_id, document_id)

        if download := self.request.query.get("download"):
            if download not in document.url:  # TODO: is this possible to download not the latest version?
                raise JsonHTTPNotFound(details="Download not found.")
            return download_file(
                document=document,
                doc_id=download,
            )
        return {"data": DocumentSerializer(document).data}

    async def patch(
        self, violation_report_id: str, document_id: str, /, body: DataModel[PatchDocument]
    ) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.decision
        """
        document, doc_index, violation_report = await self.resolve_document(violation_report_id, document_id)

        ViolationReportDecisionState.validate_decision_period(violation_report=violation_report)
        new_document = ViolationReportDecisionState.patch_document(
            violation_report,
            document=document,
            doc_index=doc_index,
            updates=body.data,
        )
        if new_document:
            await update_violation_report(violation_report)
            logger.info(
                "Violation report document patch",
                extra=get_request_logging_context({"MESSAGE_ID": "PATCH_VIOLATION_REPORT_DECISION_DOCUMENT"}),
            )
            return {"data": DocumentSerializer(new_document).data}

        return {"data": DocumentSerializer(document).data}

    async def put(
        self, violation_report_id: str, document_id: str, /, body: DataModel[PostDocument]
    ) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.decision
        """
        document, doc_index, violation_report = await self.resolve_document(violation_report_id, document_id)

        ViolationReportDecisionState.validate_decision_period(violation_report=violation_report)

        base_url = get_view_url(ViolationReportDecisionView.view_name, violation_report_id=violation_report_id)
        new_document = ViolationReportDecisionState.put_document(
            violation_report,
            base_url=base_url,
            document_data=body.data,
            document=document,
        )

        await update_violation_report(violation_report)
        logger.info(
            "Violation report document put",
            extra=get_request_logging_context({"MESSAGE_ID": "PUT_VIOLATION_REPORT_DECISION_DOCUMENT"}),
        )
        return {"data": DocumentSerializer(new_document).data}
