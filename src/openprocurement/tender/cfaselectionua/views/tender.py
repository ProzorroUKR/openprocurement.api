# -*- coding: utf-8 -*-
from copy import deepcopy
from openprocurement.api.utils import context_unpack, json_view, APIResource, get_now, raise_operation_error

from openprocurement.tender.core.utils import (
    save_tender,
    optendersresource,
    apply_patch,
    calculate_tender_business_date,
    calculate_tender_date,
)
from openprocurement.tender.core.validation import (
    validate_tender_not_in_terminated_status,
)
from openprocurement.tender.cfaselectionua.validation import (
    validate_patch_tender_in_draft_pending,
    validate_patch_tender_bot_only_in_draft_pending,
)
from openprocurement.tender.cfaselectionua.utils import (
    check_status,
    check_agreement,
    calculate_agreement_contracts_value_amount,
    calculate_tender_features,
)

from openprocurement.tender.cfaselectionua.validation import (
    validate_patch_tender_data,
    validate_json_data_in_active_enquiries,
)
from openprocurement.tender.cfaselectionua.constants import AGREEMENT_NOT_FOUND


@optendersresource(
    name="closeFrameworkAgreementSelectionUA:Tender",
    path="/tenders/{tender_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info",
)
class TenderResource(APIResource):
    @json_view(permission="view_tender")
    def get(self):
        """Tender Read

        Get Tender
        ----------

        Example request to get tender:

        .. sourcecode:: http

            GET /tenders/64e93250be76435397e8c992ed4214d1 HTTP/1.1
            Host: example.com
            Accept: application/json

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": {
                    "id": "64e93250be76435397e8c992ed4214d1",
                    "tenderID": "UA-64e93250be76435397e8c992ed4214d1",
                    "dateModified": "2014-10-27T08:06:58.158Z",
                    "procuringEntity": {
                        "id": {
                            "name": "Державне управління справами",
                            "scheme": "https://ns.openprocurement.org/ua/edrpou",
                            "uid": "00037256",
                            "uri": "http://www.dus.gov.ua/"
                        },
                        "address": {
                            "countryName": "Україна",
                            "postalCode": "01220",
                            "region": "м. Київ",
                            "locality": "м. Київ",
                            "streetAddress": "вул. Банкова, 11, корпус 1"
                        }
                    },
                    "value": {
                        "amount": 500,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    },
                    "itemsToBeProcured": [
                        {
                            "description": "футляри до державних нагород",
                            "primaryClassification": {
                                "scheme": "CPV",
                                "id": "44617100-9",
                                "description": "Cartons"
                            },
                            "additionalClassification": [
                                {
                                    "scheme": "ДКПП",
                                    "id": "17.21.1",
                                    "description": "папір і картон гофровані, паперова й картонна тара"
                                }
                            ],
                            "unitOfMeasure": "item",
                            "quantity": 5
                        }
                    ],
                    "enquiryPeriod": {
                        "endDate": "2014-10-31T00:00:00"
                    },
                    "tenderPeriod": {
                        "startDate": "2014-11-03T00:00:00",
                        "endDate": "2014-11-06T10:00:00"
                    },
                    "awardPeriod": {
                        "endDate": "2014-11-13T00:00:00"
                    },
                    "deliveryDate": {
                        "endDate": "2014-11-20T00:00:00"
                    },
                    "minimalStep": {
                        "amount": 35,
                        "currency": "UAH"
                    }
                }
            }

        """
        if self.request.authenticated_role == "chronograph":
            tender_data = self.context.serialize("chronograph_view")
        else:
            tender_data = self.context.serialize(self.context.status)
        return {"data": tender_data}

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_tender_data,
            validate_tender_not_in_terminated_status,
            validate_patch_tender_in_draft_pending,
            validate_patch_tender_bot_only_in_draft_pending,
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
        elif self.request.authenticated_role == "agreement_selection":
            apply_patch(self.request, save=False, src=self.request.validated["tender_src"])
            if self.request.tender.status == "active.enquiries":
                check_agreement(self.request, tender)
                if tender.status == "active.enquiries":
                    tender.enquiryPeriod.startDate = get_now()
                    tender.enquiryPeriod.endDate = calculate_tender_business_date(
                        tender.enquiryPeriod.startDate, self.request.content_configurator.enquiry_period, tender
                    )
                    tender.tenderPeriod.startDate = tender.enquiryPeriod.endDate
                    tender.tenderPeriod.endDate = calculate_tender_business_date(
                        tender.tenderPeriod.startDate, self.request.content_configurator.tender_period, tender
                    )
                    calculate_agreement_contracts_value_amount(self.request, tender)
                    tender.lots[0].minimalStep = deepcopy(tender.lots[0].value)
                    tender.lots[0].minimalStep.amount = round(
                        self.request.content_configurator.minimal_step_percentage * tender.lots[0].value.amount, 2
                    )
                    calculate_tender_features(self.request, tender)
            else:
                self.LOGGER.info(
                    "Switched tender {} to {}".format(tender.id, "draft.unsuccessful"),
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": "switched_tender_draft.unsuccessful"},
                        {"CAUSE": AGREEMENT_NOT_FOUND},
                    ),
                )
                tender.unsuccessfulReason = [AGREEMENT_NOT_FOUND]
        elif self.request.authenticated_role == "tender_owner" and tender.status == "active.enquiries":
            validate_json_data_in_active_enquiries(self.request)
            apply_patch(self.request, save=False, data=self.request.validated["data"])
            if "items" in self.request.validated["json_data"]:
                calculate_agreement_contracts_value_amount(self.request, tender)
        else:
            default_status = type(tender).fields["status"].default
            tender_status = tender.status
            apply_patch(self.request, save=False, src=self.request.validated["tender_src"])
            if tender_status == default_status and tender.status == "draft.pending":
                if not tender.agreements or not tender.items:
                    raise_operation_error(
                        self.request, "Can't switch tender to (draft.pending) status without agreements or items."
                    )
            if tender_status == default_status and tender.status not in ("draft.pending", default_status):
                raise_operation_error(
                    self.request, "Can't switch tender from ({}) to ({}) status.".format(default_status, tender.status)
                )
        save_tender(self.request)
        self.LOGGER.info(
            "Updated tender {}".format(tender.id), extra=context_unpack(self.request, {"MESSAGE_ID": "tender_patch"})
        )
        return {"data": tender.serialize(tender.status)}
