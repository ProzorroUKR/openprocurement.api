# -*- coding: utf-8 -*-
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.tender.core.utils import\
    save_tender, optendersresource, apply_patch
from openprocurement.tender.core.validation import (
    validate_tender_not_in_terminated_status,
    validate_tender_change_status_permission,
)

from openprocurement.tender.belowthreshold.views.tender import TenderResource
from openprocurement.tender.pricequotation.constants import PMT
from openprocurement.tender.pricequotation.utils import check_status
from openprocurement.tender.pricequotation.validation import validate_patch_tender_data

@optendersresource(
    name="{}:Tender".format(PMT),
    path="/tenders/{tender_id}",
    procurementMethodType=PMT,
)
class PriceQuotationTenderResource(TenderResource):
    """
    PriceQuotation tender creation and updation
    """
    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_tender_data,
            validate_tender_not_in_terminated_status,
            validate_tender_change_status_permission,
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
