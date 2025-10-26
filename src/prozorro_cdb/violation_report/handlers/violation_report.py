import logging
from typing import List, Tuple

from aiohttp.web import HTTPNotFound
from aiohttp_pydantic.oas.typing import r200, r201

from prozorro_cdb.api.context import (
    get_request_logging_context,
    get_view_url,
    url_to_absolute,
)
from prozorro_cdb.api.database.schema.document import Document
from prozorro_cdb.api.database.store import get_mongodb
from prozorro_cdb.api.errors import JsonHTTPBadRequest, JsonHTTPNotFound
from prozorro_cdb.api.handlers.base import BaseView, MongodbResourceListingAsync
from prozorro_cdb.api.handlers.schema.common import DataModel
from prozorro_cdb.api.handlers.schema.document import GetDocumentResponse
from prozorro_cdb.api.handlers.schema.feed import ListingResponseModel
from prozorro_cdb.api.middlewares import json_response
from prozorro_cdb.api.serializers.document import DocumentSerializer
from prozorro_cdb.api.storage import download_file
from prozorro_cdb.violation_report.database.helpers import (
    CreateViolationReportDuplicateError,
    create_violation_report,
    get_agreement_or_404,
    get_contract_or_404,
    get_pq_tender_or_error,
    get_tender_violation_reports,
    get_violation_report_id,
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
from prozorro_cdb.violation_report.handlers.schema.violation_report import (
    ViolationReportPatchRequestData,
    ViolationReportPostRequestData,
)
from prozorro_cdb.violation_report.serializers.violation_report import (
    ViolationReportSerializer,
)
from prozorro_cdb.violation_report.serializers.violation_report_details import (
    ViolationReportDetailsSerializer,
)
from prozorro_cdb.violation_report.state.details import ViolationReportDetailsState

logger = logging.getLogger(__name__)


class ViolationReportView(BaseView):
    view_name = "violation_report"

    async def get(self, violation_report_id: str, /) -> r200[ViolationReportDBModel]:
        """
        Tags: ViolationReports
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        return {"data": ViolationReportSerializer(violation_report).data}

    async def patch(
        self, violation_report_id: str, /, body: DataModel[ViolationReportPatchRequestData]
    ) -> r200[ViolationReportDBModel]:
        """
        Tags: ViolationReports
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        ViolationReportDetailsState.validate_update(
            violation_report=violation_report,
            request_data=body.data,
        )

        tender = await get_pq_tender_or_error(violation_report.tender_id)
        updated_report = ViolationReportDetailsState.update_object(
            tender=tender,
            violation_report=violation_report,
            request_data=body.data,
        )
        if updated_report is not None:  # we usually ignore this silently
            await update_violation_report(updated_report)
        return {"data": ViolationReportSerializer(violation_report).data}


class TenderViolationReportListView(BaseView):
    async def get(self, tender_id: str, /) -> r200[List[ViolationReportDBModel]]:
        """
        Tags: ViolationReports
        """
        reports = await get_tender_violation_reports(tender_id)
        return {"data": [ViolationReportSerializer(r).data for r in reports]}


class ContractViolationReportListView(BaseView):
    view_name = "contract_violation_report_list"

    async def get(self, contract_id: str, /) -> r200[List[ViolationReportDBModel]]:
        """
        Tags: ViolationReports
        """
        contract = await get_contract_or_404(contract_id)
        reports = await get_tender_violation_reports(
            tender_id=contract.tender_id,  # this field is indexed
            contract_id=contract.id,
        )
        return {"data": [ViolationReportSerializer(r).data for r in reports]}

    async def post(
        self, contract_id: str, /, body: DataModel[ViolationReportPostRequestData]
    ) -> r201[DataModel[ViolationReportDBModel]]:
        """
        Tags: ViolationReports
        """
        contract = await get_contract_or_404(contract_id)
        tender = await get_pq_tender_or_error(contract.tender_id)
        agreement = await get_agreement_or_404(tender.agreement.id)

        # create state and validate input
        ViolationReportDetailsState.validate_create(
            contract=contract,
            request_data=body.data,
        )

        # get increment number
        violation_report_id = await get_violation_report_id()

        # create obj
        base_url = get_view_url(ViolationReportDetailsView.view_name, violation_report_id=violation_report_id)
        report_obj = ViolationReportDetailsState.create_object(
            uid=violation_report_id,
            base_url=base_url,
            tender=tender,
            agreement=agreement,
            contract=contract,
            request_data=body.data,
        )
        try:
            violation_report = await create_violation_report(report_obj)
        except CreateViolationReportDuplicateError as e:
            raise JsonHTTPBadRequest(details="Trying to post a duplicate.", reason=e.duplicate_of)

        logger.info(
            "Violation Report created",
            extra=get_request_logging_context({"MESSAGE_ID": "CREATE_VIOLATION_REPORT"}),
        )
        return json_response(
            status=201,
            data={"data": ViolationReportSerializer(violation_report).data},
            headers={"Location": url_to_absolute(base_url)},
        )


class ViolationReportListView(MongodbResourceListingAsync):
    view_name = "violation_reports_feed"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_listing_method = get_mongodb().violation_report.list

    async def get(self) -> r200[ListingResponseModel]:
        """
        Tags: ViolationReports
        """
        return await super().get()


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
        violation_report_id: str, document_id: str
    ) -> Tuple[Document, int, ViolationReportDBModel]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        for doc_index, document in enumerate(reversed(violation_report.details.documents)):
            if document.id == document_id:
                return document, doc_index, violation_report
        else:
            raise HTTPNotFound(text="Document not found.")

    async def get(self, violation_report_id: str, document_id: str, /) -> r200[DataModel[GetDocumentResponse]]:
        """
        Tags: ViolationReports.details
        """
        document, _, violation_report = await self.resolve_document(violation_report_id, document_id)

        if download := self.request.query.get("download"):
            if download not in document.url:
                raise JsonHTTPNotFound(details="Download not found.")
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
