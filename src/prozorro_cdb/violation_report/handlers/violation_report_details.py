import logging
from typing import List, Optional, Tuple

from aiohttp.web import HTTPNoContent, HTTPNotFound
from aiohttp_pydantic.oas.typing import r200, r204

from prozorro_cdb.api.context import get_request_logging_context, get_view_url
from prozorro_cdb.api.database.schema.document import Document
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
    ViolationReportDBModel,
)
from prozorro_cdb.violation_report.handlers.schema.document import (
    PatchDocument,
    PostDocument,
)
from prozorro_cdb.violation_report.serializers.violation_report_details import (
    ViolationReportDetailsSerializer,
)
from prozorro_cdb.violation_report.state.details import ViolationReportDetailsState

logger = logging.getLogger(__name__)


class ViolationReportDetailsView(BaseView):
    view_name = "violation_report_details"

    async def get(self, violation_report_id: str, /) -> r200[ViolationReportDBModel]:
        """
        Tags: ViolationReports.details
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        return {"data": ViolationReportDetailsSerializer(violation_report.details).data}


class ViolationReportDocumentListView(BaseView):
    view_name = "violation_report_document_list"

    async def get(self, violation_report_id: str, /) -> r200[DataModel[List[Document]]]:
        """
        Tags: ViolationReports.details
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        return {"data": [DocumentSerializer(d).data for d in violation_report.details.documents]}

    async def post(self, violation_report_id: str, /, body: DataModel[PostDocument]) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.details
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        ViolationReportDetailsState.validate_post_document(violation_report, body.data)

        base_url = get_view_url(ViolationReportDetailsView.view_name, violation_report_id=violation_report_id)
        document = ViolationReportDetailsState.post_document(
            violation_report,
            base_url,
            body.data,
        )
        await update_violation_report(violation_report)
        logger.info(
            "Violation Report document post",
            extra=get_request_logging_context({"MESSAGE_ID": "POST_VIOLATION_REPORT_DETAILS_DOCUMENT"}),
        )

        return {"data": DocumentSerializer(document).data}


class ViolationReportDocumentView(BaseView):
    view_name = "violation_report_document"

    @staticmethod
    async def resolve_document(
        violation_report_id: str,
        document_id: str,
        download: Optional[str] = None,
    ) -> Tuple[Document, int, ViolationReportDBModel]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        for doc_index, document in reversed(list(enumerate(violation_report.details.documents))):
            if document.id == document_id and (download is None or download in document.url):
                return document, doc_index, violation_report
        else:
            raise HTTPNotFound(text="Document not found.")

    async def get(self, violation_report_id: str, document_id: str, /) -> r200[DataModel[GetDocumentResponse]]:
        """
        Tags: ViolationReports.details
        """
        document, _, violation_report = await self.resolve_document(
            violation_report_id, document_id, download=self.request.query.get("download")
        )
        if download := self.request.query.get("download"):
            return download_file(document=document, doc_id=download)

        document_data = document.model_dump(exclude_none=True)
        document_data["previousVersions"] = [
            DocumentSerializer(i).data
            for i in violation_report.details.documents
            if i.id == document.id and i.url != document.url
        ]
        return {"data": DocumentSerializer(document_data).data}

    async def patch(
        self, violation_report_id: str, document_id: str, /, body: DataModel[PatchDocument]
    ) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.details
        """
        document, doc_index, violation_report = await self.resolve_document(violation_report_id, document_id)

        ViolationReportDetailsState.validate_update_allowed_status(violation_report)
        new_document = ViolationReportDetailsState.patch_document(
            violation_report,
            document=document,
            doc_index=doc_index,
            updates=body.data,
        )
        if new_document:
            await update_violation_report(violation_report)
            logger.info(
                "Violation report document patch",
                extra=get_request_logging_context({"MESSAGE_ID": "PATCH_VIOLATION_REPORT_DETAILS_DOCUMENT"}),
            )
            return {"data": DocumentSerializer(new_document).data}

        return {"data": DocumentSerializer(document).data}

    async def put(
        self, violation_report_id: str, document_id: str, /, body: DataModel[PostDocument]
    ) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.details
        """
        document, doc_index, violation_report = await self.resolve_document(violation_report_id, document_id)

        ViolationReportDetailsState.validate_update_allowed_status(violation_report)
        base_url = get_view_url(ViolationReportDetailsView.view_name, violation_report_id=violation_report_id)
        new_document = ViolationReportDetailsState.put_document(
            violation_report,
            base_url=base_url,
            document_data=body.data,
            document=document,
        )

        await update_violation_report(violation_report)
        logger.info(
            "Violation report document put",
            extra=get_request_logging_context({"MESSAGE_ID": "PUT_VIOLATION_REPORT_DETAILS_DOCUMENT"}),
        )
        return {"data": DocumentSerializer(new_document).data}

    async def delete(self, violation_report_id: str, document_id: str, /) -> r204[None]:
        """
        Tags: ViolationReports.details
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        ViolationReportDetailsState.validate_update_allowed_status(violation_report)

        updated = ViolationReportDetailsState.delete_document(violation_report, document_id=document_id)
        if updated:
            await update_violation_report(violation_report)
            logger.info(
                "Violation report document delete",
                extra=get_request_logging_context({"MESSAGE_ID": "DELETE_VIOLATION_REPORT_DETAILS_DOCUMENT"}),
            )
        return HTTPNoContent()
