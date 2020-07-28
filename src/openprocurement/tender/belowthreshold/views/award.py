# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now, json_view, APIResource, context_unpack, raise_operation_error

from openprocurement.tender.core.utils import (
    save_tender,
    optendersresource,
    apply_patch,
    calculate_tender_business_date,
)

from openprocurement.tender.core.validation import (
    validate_award_data,
    validate_patch_award_data,
    validate_update_award_only_for_active_lots,
    validate_update_award_in_not_allowed_status,
)

from openprocurement.tender.belowthreshold.constants import STAND_STILL_TIME

from openprocurement.tender.belowthreshold.utils import add_next_award, add_contract

from openprocurement.tender.belowthreshold.validation import (
    validate_create_award_only_for_active_lot,
    validate_create_award_not_in_allowed_period,
)


@optendersresource(
    name="belowThreshold:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="belowThreshold",
)
class TenderAwardResource(APIResource):
    @json_view(permission="view_tender")
    def collection_get(self):
        """Tender Awards List

        Get Awards List
        ---------------

        Example request to get awards list:

        .. sourcecode:: http

            GET /tenders/4879d3f8ee2443169b5fbbc9f89fa607/awards HTTP/1.1
            Host: example.com
            Accept: application/json

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": [
                    {
                        "status": "active",
                        "suppliers": [
                            {
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
                            }
                        ],
                        "value": {
                            "amount": 489,
                            "currency": "UAH",
                            "valueAddedTaxIncluded": true
                        }
                    }
                ]
            }

        """
        return {"data": [i.serialize("view") for i in self.request.validated["tender"].awards]}

    @json_view(
        content_type="application/json",
        permission="create_award",
        validators=(
            validate_award_data,
            validate_create_award_not_in_allowed_period,
            validate_create_award_only_for_active_lot,
        ),
    )
    def collection_post(self):
        """Accept or reject bidder application

        Creating new Award
        ------------------

        Example request to create award:

        .. sourcecode:: http

            POST /tenders/4879d3f8ee2443169b5fbbc9f89fa607/awards HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "status": "active",
                    "suppliers": [
                        {
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
                        }
                    ],
                    "value": {
                        "amount": 489,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 201 Created
            Content-Type: application/json

            {
                "data": {
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "date": "2014-10-28T11:44:17.947Z",
                    "status": "active",
                    "suppliers": [
                        {
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
                        }
                    ],
                    "value": {
                        "amount": 489,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        tender = self.request.validated["tender"]
        award = self.request.validated["award"]
        tender.awards.append(award)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender award {}".format(award.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_award_create"}, {"award_id": award.id}),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Awards".format(tender.procurementMethodType), tender_id=tender.id, award_id=award["id"]
            )

            return {"data": award.serialize("view")}

    @json_view(permission="view_tender")
    def get(self):
        """Retrieving the award

        Example request for retrieving the award:

        .. sourcecode:: http

            GET /tenders/4879d3f8ee2443169b5fbbc9f89fa607/awards/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
            Host: example.com
            Accept: application/json

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

            {
                "data": {
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "date": "2014-10-28T11:44:17.947Z",
                    "status": "active",
                    "suppliers": [
                        {
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
                        }
                    ],
                    "value": {
                        "amount": 489,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        return {"data": self.request.validated["award"].serialize("view")}

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_patch_award_data,
            validate_update_award_in_not_allowed_status,
            validate_update_award_only_for_active_lots,
        ),
    )
    def patch(self):
        """Update of award

        Example request to change the award:

        .. sourcecode:: http

            PATCH /tenders/4879d3f8ee2443169b5fbbc9f89fa607/awards/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "value": {
                        "amount": 600
                    }
                }
            }

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

            {
                "data": {
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "date": "2014-10-28T11:44:17.947Z",
                    "status": "active",
                    "suppliers": [
                        {
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
                        }
                    ],
                    "value": {
                        "amount": 600,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        tender = self.request.validated["tender"]
        award = self.request.context
        award_status = award.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())

        now = get_now()

        if award_status != award.status and award.status in ["active", "unsuccessful"]:
            if award.complaintPeriod:
                award.complaintPeriod.startDate = now
            else:
                award.complaintPeriod = {"startDate": now.isoformat()}

        if award_status == "pending" and award.status == "active":
            award.complaintPeriod.endDate = calculate_tender_business_date(now, STAND_STILL_TIME, tender, True)
            add_contract(self.request, award, now)
            add_next_award(self.request)
        elif award_status == "active" and award.status == "cancelled":
            if award.complaintPeriod.endDate > now:
                award.complaintPeriod.endDate = now
            for j in award.complaints:
                if j.status not in ["invalid", "resolved", "declined"]:
                    j.status = "cancelled"
                    j.cancellationReason = "cancelled"
                    j.dateCanceled = now
            for i in tender.contracts:
                if i.awardID == award.id:
                    i.status = "cancelled"
            add_next_award(self.request)
        elif award_status == "pending" and award.status == "unsuccessful":
            award.complaintPeriod.endDate = calculate_tender_business_date(get_now(), STAND_STILL_TIME, tender, True)
            add_next_award(self.request)
        elif (
            award_status == "unsuccessful"
            and award.status == "cancelled"
            and any([i.status in ["claim", "answered", "pending", "resolved"] for i in award.complaints])
        ):
            if tender.status == "active.awarded":
                tender.status = "active.qualification"
                tender.awardPeriod.endDate = None
            award.complaintPeriod.endDate = now
            cancelled_awards = []
            for i in tender.awards[tender.awards.index(award):]:
                if i.lotID != award.lotID:
                    continue
                if i.complaintPeriod and (not i.complaintPeriod.endDate or i.complaintPeriod.endDate > now):
                    i.complaintPeriod.endDate = now
                i.status = "cancelled"
                for j in i.complaints:
                    if j.status not in ["invalid", "resolved", "declined"]:
                        j.status = "cancelled"
                        j.cancellationReason = "cancelled"
                        j.dateCanceled = now
                cancelled_awards.append(i.id)
            for i in tender.contracts:
                if i.awardID in cancelled_awards:
                    i.status = "cancelled"
            add_next_award(self.request)
        elif self.request.authenticated_role != "Administrator" and not (
            award_status == "pending" and award.status == "pending"
        ):
            raise_operation_error(self.request, "Can't update award in current ({}) status".format(award_status))
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender award {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_award_patch"}),
            )
            return {"data": award.serialize("view")}
