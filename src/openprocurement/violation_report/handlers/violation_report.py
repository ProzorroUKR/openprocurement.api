import logging
from typing import List

from aiohttp.web import HTTPNotFound
from aiohttp_pydantic.oas.typing import r200, r201

from openprocurement.api.context_async import (
    get_request_logging_context,
    get_view_url,
    url_to_absolute,
)
from openprocurement.api.database_async import get_mongodb
from openprocurement.api.errors_async import JsonHTTPBadRequest, JsonHTTPNotFound
from openprocurement.api.handlers.base import BaseView, MongodbResourceListingAsync
from openprocurement.api.middlewares_async import json_response
from openprocurement.api.models_async.common import DataModel
from openprocurement.api.models_async.document import Document
from openprocurement.api.serializers_async.document import DocumentSerializer
from openprocurement.api.storage_async import download_file
from openprocurement.violation_report.database.helpers import (
    CreateViolationReportDuplicateError,
    create_violation_report,
    get_contract_or_404,
    get_tender_violation_reports,
    get_violation_report_id,
    get_violation_report_or_404,
)
from openprocurement.violation_report.database.schema.violation_report import (
    ViolationReportDBModel,
)
from openprocurement.violation_report.handlers.schema.violation_report import (
    ViolationReportDraftRequestData,
)
from openprocurement.violation_report.serializers.violation_report import (
    ViolationReportSerializer,
)
from openprocurement.violation_report.state.draft import ViolationReportDraftState

logger = logging.getLogger(__name__)


class ViolationReportDetailsView(BaseView):
    view_name = "violation_report_details"

    async def get(self, violation_report_id: str, /) -> r200[ViolationReportDBModel]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        return {"data": ViolationReportSerializer(violation_report).data}


class TenderViolationReportListView(BaseView):
    async def get(self, tender_id: str, /) -> r200[List[ViolationReportDBModel]]:
        reports = await get_tender_violation_reports(tender_id)
        return {"data": [ViolationReportSerializer(r).data for r in reports]}


class ContractViolationReportListView(BaseView):
    view_name = "contract_violation_report_list"

    async def get(self, contract_id: str, /) -> r200[List[ViolationReportDBModel]]:
        contract = await get_contract_or_404(contract_id)
        reports = await get_tender_violation_reports(tender_id=contract.tender_id, contract_id=contract.id)
        return {"data": [ViolationReportSerializer(r).data for r in reports]}

    async def post(
        self, contract_id: str, /, body: DataModel[ViolationReportDraftRequestData]
    ) -> r201[DataModel[ViolationReportDBModel]]:
        contract = await get_contract_or_404(contract_id)

        # create state and validate input
        state = ViolationReportDraftState(contract=contract, data=body.data)

        # get increment number
        violation_report_id = await get_violation_report_id()

        # create db obj
        base_url = get_view_url(ViolationReportDetailsView.view_name, violation_report_id=violation_report_id)
        report_obj = state.create_from_user_input(uid=violation_report_id, base_url=base_url)

        try:
            violation_report = await create_violation_report(report_obj)
        except CreateViolationReportDuplicateError as e:
            raise JsonHTTPBadRequest(message="Trying to post a duplicate.", reason=e.duplicate_of)

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
        self.db_listing_method = get_mongodb().violation_reports.list


class ViolationReportDocumentView(BaseView):
    view_name = "violation_report_document"

    async def get(self, violation_report_id: str, document_id: str, /) -> r200[DataModel[Document]]:
        violation_report = await get_violation_report_or_404(violation_report_id)

        for document in violation_report.documents:
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
