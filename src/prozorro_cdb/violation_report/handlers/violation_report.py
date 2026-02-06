import logging
from typing import List, Union
from uuid import uuid4

from aiohttp_pydantic.oas.typing import r200, r201

from prozorro_cdb.api.context import (
    get_request_logging_context,
    get_view_url,
    url_to_absolute,
)
from prozorro_cdb.api.database.store import get_mongodb
from prozorro_cdb.api.handlers.base import BaseView, MongodbResourceListingAsync
from prozorro_cdb.api.handlers.schema.common import DataModel
from prozorro_cdb.api.handlers.schema.feed import ListingResponseModel
from prozorro_cdb.api.middlewares import json_response
from prozorro_cdb.violation_report.database.helpers import (
    create_violation_report,
    get_agreement_or_404,
    get_contract_or_404,
    get_pq_tender_or_error,
    get_tender_violation_reports,
    get_violation_report_or_404,
    get_violation_report_pretty_id,
    update_violation_report,
)
from prozorro_cdb.violation_report.database.schema.violation_report import (
    ViolationReportDBModel,
    ViolationReportStatus,
)
from prozorro_cdb.violation_report.handlers.schema.violation_report import (
    ViolationReportPatchDetailsRequestData,
    ViolationReportPostRequestData,
    ViolationReportPublishRequestData,
)
from prozorro_cdb.violation_report.serializers.violation_report import (
    ViolationReportSerializer,
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
        self,
        violation_report_id: str,
        /,
        body: DataModel[Union[ViolationReportPatchDetailsRequestData, ViolationReportPublishRequestData]],
    ) -> r200[ViolationReportDBModel]:
        """
        Tags: ViolationReports
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        ViolationReportDetailsState.validate_update_allowed_status(violation_report)
        if (
            isinstance(body.data, ViolationReportPublishRequestData)
            and violation_report.status == ViolationReportStatus.draft
        ):
            ViolationReportDetailsState.validate_publish(
                violation_report=violation_report,
            )
            tender = await get_pq_tender_or_error(violation_report.tender_id)
            ViolationReportDetailsState.publish_report(
                tender=tender,
                violation_report=violation_report,
            )
            await update_violation_report(violation_report, modified=True)

        elif isinstance(body.data, ViolationReportPatchDetailsRequestData):
            updated_report = ViolationReportDetailsState.update_details(
                violation_report=violation_report,
                request_data=body.data,
            )
            if updated_report is not None:  # we usually ignore this silently
                await update_violation_report(updated_report, modified=False)

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
        ViolationReportDetailsState.validate_create(request_data=body.data)

        # get ids
        violation_report_id = uuid4().hex
        violation_report_pretty_id = await get_violation_report_pretty_id()

        # create obj
        base_url = get_view_url(ViolationReportView.view_name, violation_report_id=violation_report_id)
        report_obj = ViolationReportDetailsState.create_object(
            uid=violation_report_id,
            pretty_id=violation_report_pretty_id,
            base_url=base_url,
            tender=tender,
            agreement=agreement,
            contract=contract,
            request_data=body.data,
        )
        violation_report = await create_violation_report(report_obj)
        logger.info(
            "Violation Report created",
            extra=get_request_logging_context(
                {
                    "MESSAGE_ID": "CREATE_VIOLATION_REPORT",
                    "violation_report_id": report_obj.id,
                }
            ),
        )
        return json_response(
            status=201,
            data={"data": ViolationReportSerializer(violation_report).data},
            headers={"Location": url_to_absolute(base_url)},
        )


class ViolationReportListView(MongodbResourceListingAsync):
    view_name = "violation_reports_feed"
    listing_allowed_fields = {
        "public_modified",
        "dateCreated",
        "dateModified",
        "datePublished",
        "status",
        "violationReportID",
        "tender_id",
        "contract_id",
        "author",
        "defendants",
        "authority",
        "defendantPeriod",
        "defendantStatements",
        "decisions",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_listing_method = get_mongodb().violation_report.list

    async def get(self) -> r200[ListingResponseModel]:
        """
        Tags: ViolationReports
        """
        return await super().get()
