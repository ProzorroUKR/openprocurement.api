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
from openprocurement.api.models_async.document import Document, RequestDocument
from openprocurement.api.serializers_async.document import DocumentSerializer
from openprocurement.api.storage_async import download_file
from openprocurement.violation_report.database.helpers import (
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
from openprocurement.violation_report.database.schema.violation_report import (
    ViolationReportDBModel,
)
from openprocurement.violation_report.handlers.schema.violation_report import (
    ViolationReportPatchRequestData,
    ViolationReportPostRequestData,
)
from openprocurement.violation_report.serializers.violation_report import (
    ViolationReportSerializer,
)
from openprocurement.violation_report.serializers.violation_report_details import (
    ViolationReportDetailsSerializer,
)
from openprocurement.violation_report.state.details import ViolationReportDetailsState

logger = logging.getLogger(__name__)


class ViolationReportView(BaseView):
    view_name = "violation_report"

    async def get(self, violation_report_id: str, /) -> r200[ViolationReportDBModel]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        return {"data": ViolationReportSerializer(violation_report).data}

    async def patch(
        self, violation_report_id: str, /, body: DataModel[ViolationReportPatchRequestData]
    ) -> r200[ViolationReportDBModel]:
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


class ViolationReportDetailsView(BaseView):
    view_name = "violation_report_details"

    async def get(self, violation_report_id: str, /) -> r200[ViolationReportDBModel]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        return {"data": ViolationReportDetailsSerializer(violation_report.details).data}


class TenderViolationReportListView(BaseView):
    async def get(self, tender_id: str, /) -> r200[List[ViolationReportDBModel]]:
        reports = await get_tender_violation_reports(tender_id)
        return {"data": [ViolationReportSerializer(r).data for r in reports]}


class ContractViolationReportListView(BaseView):
    view_name = "contract_violation_report_list"

    async def get(self, contract_id: str, /) -> r200[List[ViolationReportDBModel]]:
        contract = await get_contract_or_404(contract_id)
        reports = await get_tender_violation_reports(
            tender_id=contract.tender_id,  # this field is indexed
            contract_id=contract.id,
        )
        return {"data": [ViolationReportSerializer(r).data for r in reports]}

    async def post(
        self, contract_id: str, /, body: DataModel[ViolationReportPostRequestData]
    ) -> r201[DataModel[ViolationReportDBModel]]:
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
        self.db_listing_method = get_mongodb().violation_reports.list


class ViolationReportDocumentListView(BaseView):
    view_name = "violation_report_document_list"

    async def get(self, violation_report_id: str, /) -> r200[DataModel[List[Document]]]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        return {"data": [DocumentSerializer(d).data for d in violation_report.details.documents]}

    async def post(self, violation_report_id: str, /, body: DataModel[RequestDocument]) -> r200[DataModel[Document]]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        ViolationReportDetailsState.validate_add_details_document(violation_report, body.data)

        base_url = get_view_url(ViolationReportDetailsView.view_name, violation_report_id=violation_report_id)
        document = ViolationReportDetailsState.add_details_document(
            violation_report,
            base_url,
            body.data,
        )
        await update_violation_report(violation_report)

        return {"data": DocumentSerializer(document).data}


class ViolationReportDocumentView(BaseView):
    view_name = "violation_report_document"

    async def get(self, violation_report_id: str, document_id: str, /) -> r200[DataModel[Document]]:
        violation_report = await get_violation_report_or_404(violation_report_id)

        for document in violation_report.details.documents:
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
