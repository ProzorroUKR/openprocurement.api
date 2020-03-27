# -*- coding: utf-8 -*-
from openprocurement.tender.core.validation import (
    validate_patch_tender_data,
    validate_tender_not_in_terminated_status,
    validate_tender_change_status_with_cancellation_lot_pending,
)
from openprocurement.api.utils import json_view, context_unpack
from openprocurement.tender.core.utils import apply_patch, optendersresource, save_tender
from openprocurement.tender.belowthreshold.views.tender import TenderResource as BaseTenderResource
from openprocurement.tender.limited.validation import (
    validate_chronograph,
    validate_chronograph_before_2020_04_19,
    validate_update_tender_with_awards,
)
from openprocurement.tender.limited.utils import check_status


@optendersresource(
    name="reporting:Tender",
    path="/tenders/{tender_id}",
    procurementMethodType="reporting",
    description="Open Contracting compatible data exchange format. See "
                "http://ocds.open-contracting.org/standard/r/master/#tender for more info",
)
class TenderResource(BaseTenderResource):
    """ Resource handler for TenderLimited """

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_tender_data,
            validate_tender_not_in_terminated_status,
            validate_chronograph,
            validate_update_tender_with_awards,
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
        tender = self.request.validated["tender"]
        data = self.request.validated["data"]
        apply_patch(self.request, data=data, src=self.request.validated["tender_src"])
        self.LOGGER.info(
            "Updated tender {}".format(tender.id), extra=context_unpack(self.request, {"MESSAGE_ID": "tender_patch"})
        )
        return {"data": tender.serialize(tender.status)}


@optendersresource(
    name="negotiation:Tender",
    path="/tenders/{tender_id}",
    procurementMethodType="negotiation",
    description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info",
)
class TenderNegotioationResource(TenderResource):
    """ Resource handler for Negotiation Tender """

    @json_view(
        content_type="application/json",
        validators=(
                validate_patch_tender_data,
                validate_chronograph_before_2020_04_19,
                validate_tender_not_in_terminated_status,
                validate_update_tender_with_awards,
                validate_tender_change_status_with_cancellation_lot_pending
        ),
        permission="edit_tender",
    )
    def patch(self):

        tender = self.context
        if self.request.authenticated_role == "chronograph":
            apply_patch(self.request, save=False, src=self.request.validated["tender_src"])
            check_status(self.request)
            save_tender(self.request)
        else:
            apply_patch(self.request, src=self.request.validated["tender_src"])
        self.LOGGER.info(
            "Updated tender {}".format(tender.id), extra=context_unpack(self.request, {"MESSAGE_ID": "tender_patch"})
        )
        return {"data": tender.serialize(tender.status)}


@optendersresource(
    name="negotiation.quick:Tender",
    path="/tenders/{tender_id}",
    procurementMethodType="negotiation.quick",
    description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info",
)
class TenderNegotioationQuickResource(TenderNegotioationResource):
    """ Resource handler for Negotiation Quick Tender """
