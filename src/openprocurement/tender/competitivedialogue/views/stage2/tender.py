# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view, context_unpack, get_now, raise_operation_error
from openprocurement.tender.core.utils import (
    optendersresource,
    save_tender,
    apply_patch,
    calculate_tender_business_date,
)
from openprocurement.tender.core.validation import (
    validate_tender_period_extension,
    validate_tender_not_in_terminated_status,
    validate_tender_status_update_not_in_pre_qualificaton,
    validate_tender_change_status_with_cancellation_lot_pending,
)
from openprocurement.tender.openua.views.tender import TenderUAResource
from openprocurement.tender.openeu.views.tender import TenderEUResource
from openprocurement.tender.openeu.constants import PREQUALIFICATION_COMPLAINT_STAND_STILL as COMPLAINT_STAND_STILL
from openprocurement.tender.openeu.utils import check_status as check_status_eu, all_bids_are_reviewed
from openprocurement.tender.openua.utils import check_status as check_status_ua
from openprocurement.tender.competitivedialogue.validation import validate_patch_tender_stage2_data
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE, STAGE2_STATUS
from openprocurement.tender.core.events import TenderInitializeEvent


@optendersresource(
    name="{}:Tender".format(STAGE_2_UA_TYPE),
    path="/tenders/{tender_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="",
)
class TenderStage2UAResource(TenderUAResource):
    """ Resource handler for tender stage 2 UA"""

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_tender_stage2_data,
            validate_tender_not_in_terminated_status,
            validate_tender_change_status_with_cancellation_lot_pending,
        ),
        permission="edit_tender",
    )
    def patch(self):
        """Tender Edit (partial)

        For example here is how procuring entity can change number of items to be procured and total Value of a tender:

        .. sourcecode:: http

            PATCH /tenders/4879d3f8ee2443169b5fbbc9f89fa607 HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "value": {
                        "amount": 600
                    },
                    "itemsToBeProcured": [
                        {
                            "quantity": 6
                        }
                    ]
                }
            }

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

            {
                "data": {
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "tenderID": "UA-64e93250be76435397e8c992ed4214d1",
                    "dateModified": "2014-10-27T08:12:34.956Z",
                    "value": {
                        "amount": 600
                    },
                    "itemsToBeProcured": [
                        {
                            "quantity": 6
                        }
                    ]
                }
            }

        """
        tender = self.context
        data = self.request.validated["data"]

        if self.request.authenticated_role == "tender_owner" and self.request.validated["tender_status"] in [
            "active.tendering",
            STAGE2_STATUS,
        ]:
            if "tenderPeriod" in data and "endDate" in data["tenderPeriod"]:
                self.request.validated["tender"].tenderPeriod.import_data(data["tenderPeriod"])
                validate_tender_period_extension(self.request)
                self.request.registry.notify(TenderInitializeEvent(self.request.validated["tender"]))
                self.request.validated["data"]["enquiryPeriod"] = self.request.validated[
                    "tender"
                ].enquiryPeriod.serialize()

        apply_patch(self.request, save=False, src=self.request.validated["tender_src"])
        if self.request.authenticated_role == "chronograph":
            check_status_ua(self.request)
        elif self.request.authenticated_role == "tender_owner" and tender.status == "active.tendering":
            # invalidate bids on tender change
            tender.invalidate_bids_data()
        save_tender(self.request)
        self.LOGGER.info(
            "Updated tender {}".format(tender.id), extra=context_unpack(self.request, {"MESSAGE_ID": "tender_patch"})
        )
        return {"data": tender.serialize(tender.status)}


@optendersresource(
    name="{}:Tender".format(STAGE_2_EU_TYPE),
    path="/tenders/{tender_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="",
)
class TenderStage2UEResource(TenderEUResource):
    """ Resource handler for tender stage 2 EU"""

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_tender_stage2_data,
            validate_tender_not_in_terminated_status,
            validate_tender_status_update_not_in_pre_qualificaton,
            validate_tender_change_status_with_cancellation_lot_pending,
        ),
        permission="edit_tender",
    )
    def patch(self):
        """Tender Edit (partial)

        For example here is how procuring entity can change number of items to be procured and total Value of a tender:

        .. sourcecode:: http

            PATCH /tenders/4879d3f8ee2443169b5fbbc9f89fa607 HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "value": {
                        "amount": 600
                    },
                    "itemsToBeProcured": [
                        {
                            "quantity": 6
                        }
                    ]
                }
            }

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

            {
                "data": {
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "tenderID": "UA-64e93250be76435397e8c992ed4214d1",
                    "dateModified": "2014-10-27T08:12:34.956Z",
                    "value": {
                        "amount": 600
                    },
                    "itemsToBeProcured": [
                        {
                            "quantity": 6
                        }
                    ]
                }
            }

        """
        tender = self.context
        data = self.request.validated["data"]
        if self.request.authenticated_role == "tender_owner" and self.request.validated["tender_status"] in [
            "active.tendering",
            STAGE2_STATUS,
        ]:
            if "tenderPeriod" in data and "endDate" in data["tenderPeriod"]:
                self.request.validated["tender"].tenderPeriod.import_data(data["tenderPeriod"])
                validate_tender_period_extension(self.request)
                self.request.registry.notify(TenderInitializeEvent(self.request.validated["tender"]))
                self.request.validated["data"]["enquiryPeriod"] = self.request.validated[
                    "tender"
                ].enquiryPeriod.serialize()

        apply_patch(self.request, save=False, src=self.request.validated["tender_src"])
        if self.request.authenticated_role == "chronograph":
            check_status_eu(self.request)
        elif self.request.authenticated_role == "tender_owner" and tender.status == "active.tendering":
            tender.invalidate_bids_data()
        elif (
            self.request.authenticated_role == "tender_owner"
            and self.request.validated["tender_status"] == "active.pre-qualification"
            and tender.status == "active.pre-qualification.stand-still"
        ):
            if all_bids_are_reviewed(self.request):
                tender.qualificationPeriod.endDate = calculate_tender_business_date(
                    get_now(), COMPLAINT_STAND_STILL, self.request.validated["tender"]
                )
                tender.check_auction_time()
            else:
                raise_operation_error(
                    self.request,
                    "Can't switch to 'active.pre-qualification.stand-still' while not all bids are qualified",
                )

        save_tender(self.request)
        self.LOGGER.info(
            "Updated tender {}".format(tender.id), extra=context_unpack(self.request, {"MESSAGE_ID": "tender_patch"})
        )
        return {"data": tender.serialize(tender.status)}
