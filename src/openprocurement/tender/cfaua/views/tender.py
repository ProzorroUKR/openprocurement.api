# -*- coding: utf-8 -*-
from zope.component import getAdapter

from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.api.utils import json_view, context_unpack, get_now, raise_operation_error
from openprocurement.tender.core.utils import (
    optendersresource,
    apply_patch,
    save_tender,
    calculate_complaint_business_date,
)
from openprocurement.tender.core.validation import (
    validate_tender_period_extension,
    validate_tender_not_in_terminated_status,
    validate_tender_change_status_with_cancellation_lot_pending,
)
from openprocurement.tender.belowthreshold.views.tender import TenderResource
from openprocurement.tender.cfaua.utils import check_status, all_bids_are_reviewed, all_awards_are_reviewed
from openprocurement.tender.openua.validation import validate_patch_tender_ua_data
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.tender.cfaua.validation import validate_tender_status_update


@optendersresource(
    name="closeFrameworkAgreementUA:Tender",
    path="/tenders/{tender_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Open Contracting compatible data exchange format. "
    "See http://ocds.open-contracting.org/standard/r/master/#tender for more info",
)
class TenderEUResource(TenderResource):
    """ Resource handler for TenderEU """

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_tender_ua_data,
            validate_tender_not_in_terminated_status,
            validate_tender_status_update,
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
        config = getAdapter(tender, IContentConfigurator)
        data = self.request.validated["data"]
        now = get_now()
        if (
            self.request.authenticated_role == "tender_owner"
            and self.request.validated["tender_status"] == "active.tendering"
        ):
            if "tenderPeriod" in data and "endDate" in data["tenderPeriod"]:
                self.request.validated["tender"].tenderPeriod.import_data(data["tenderPeriod"])
                validate_tender_period_extension(self.request)
                self.request.registry.notify(TenderInitializeEvent(self.request.validated["tender"]))
                self.request.validated["data"]["enquiryPeriod"] = self.request.validated[
                    "tender"
                ].enquiryPeriod.serialize()

        apply_patch(self.request, save=False, src=self.request.validated["tender_src"])
        if self.request.authenticated_role == "chronograph":
            check_status(self.request)
        elif self.request.authenticated_role == "tender_owner" and tender.status == "active.tendering":
            tender.invalidate_bids_data()
        elif (
            self.request.authenticated_role == "tender_owner"
            and self.request.validated["tender_status"] == "active.pre-qualification"
            and tender.status == "active.pre-qualification.stand-still"
        ):
            active_lots = [lot.id for lot in tender.lots if lot.status == "active"] if tender.lots else [None]
            if any(
                [
                    i["status"] in self.request.validated["tender"].block_complaint_status
                    for q in self.request.validated["tender"]["qualifications"]
                    for i in q["complaints"]
                    if q["lotID"] in active_lots
                ]
            ):
                raise_operation_error(
                    self.request, "Can't switch to 'active.pre-qualification.stand-still' before resolve all complaints"
                )
            if all_bids_are_reviewed(self.request):
                tender.qualificationPeriod.endDate = calculate_complaint_business_date(
                    now, config.prequalification_complaint_stand_still, self.request.validated["tender"]
                )
                tender.check_auction_time()
            else:
                raise_operation_error(
                    self.request,
                    "Can't switch to 'active.pre-qualification.stand-still' while not all bids are qualified",
                )
        elif (
            self.request.authenticated_role == "tender_owner"
            and self.request.validated["tender_status"] == "active.qualification"
            and tender.status == "active.qualification.stand-still"
        ):
            active_lots = [lot.id for lot in tender.lots if lot.status == "active"] if tender.lots else [None]
            if any(
                [
                    i["status"] in self.request.validated["tender"].block_complaint_status
                    for a in self.request.validated["tender"]["awards"]
                    for i in a["complaints"]
                    if a["lotID"] in active_lots
                ]
            ):
                raise_operation_error(
                    self.request, "Can't switch to 'active.qualification.stand-still' before resolve all complaints"
                )
            if all_awards_are_reviewed(self.request):
                tender.awardPeriod.endDate = calculate_complaint_business_date(
                    now, config.qualification_complaint_stand_still, self.request.validated["tender"]
                )
                for award in [a for a in tender.awards if a.status != "cancelled"]:
                    award["complaintPeriod"] = {
                        "startDate": now.isoformat(),
                        "endDate": tender.awardPeriod.endDate.isoformat(),
                    }
            else:
                raise_operation_error(
                    self.request,
                    "Can't switch to 'active.qualification.stand-still' while not all awards are qualified",
                )

        save_tender(self.request)
        self.LOGGER.info(
            "Updated tender {}".format(tender.id), extra=context_unpack(self.request, {"MESSAGE_ID": "tender_patch"})
        )
        return {"data": tender.serialize(tender.status)}
