# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now, raise_operation_error
from openprocurement.tender.belowthreshold.utils import add_contracts, set_award_contracts_cancelled

from openprocurement.tender.core.utils import (
    apply_patch,
    optendersresource,
    save_tender,
)

from openprocurement.tender.core.validation import (
    validate_patch_award_data,
    validate_update_award_only_for_active_lots,
    validate_update_award_in_not_allowed_status,
    validate_update_award_with_accepted_complaint,
    validate_operation_with_lot_cancellation_in_pending,
    validate_update_status_before_milestone_due_date,
)
from openprocurement.tender.belowthreshold.views.award import TenderAwardResource
from openprocurement.api.utils import json_view, context_unpack, get_first_revision_date
from openprocurement.api.constants import NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO
from openprocurement.tender.openuadefense.constants import STAND_STILL_TIME
from openprocurement.tender.openuadefense.utils import add_next_award
from openprocurement.tender.openuadefense.utils import calculate_complaint_business_date


@optendersresource(
    name="aboveThresholdUA.defense:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="aboveThresholdUA.defense",
)
class TenderUaAwardResource(TenderAwardResource):
    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_patch_award_data,
            validate_update_award_in_not_allowed_status,
            validate_update_award_only_for_active_lots,
            validate_operation_with_lot_cancellation_in_pending("award"),
            validate_update_award_with_accepted_complaint,
            validate_update_status_before_milestone_due_date,
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
        first_revision_date = get_first_revision_date(tender)
        new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < first_revision_date < NEW_DEFENSE_COMPLAINTS_TO

        if award_status == "pending" and award.status == "active":

            complaint_end_date = calculate_complaint_business_date(now, STAND_STILL_TIME, tender, True)
            award.complaintPeriod = {
                "startDate": now.isoformat(),
                "endDate": complaint_end_date,
            }

            if new_defence_complaints:
                for i in tender.awards:
                    if i.lotID != award.lotID:
                        continue
                    if i.status != "unsuccessful":
                        continue
                    i.complaintPeriod = {
                        "startDate": now.isoformat(),
                        "endDate": complaint_end_date,
                    }

            add_contracts(self.request, award, now)
            add_next_award(self.request)
        elif (
            award_status == "active"
            and award.status == "cancelled"
            and any([i.status == "satisfied" for i in award.complaints])
        ):
            for i in tender.awards:
                if i.lotID != award.lotID:
                    continue
                if (
                    not new_defence_complaints
                    and i.complaintPeriod
                    and (not i.complaintPeriod.endDate or i.complaintPeriod.endDate > now)
                ):
                    i.complaintPeriod.endDate = now
                i.status = "cancelled"
                set_award_contracts_cancelled(self.request, i)
            add_next_award(self.request)
        elif award_status == "active" and award.status == "cancelled":
            if (
                not new_defence_complaints
                and award.complaintPeriod.endDate > now
            ):
                award.complaintPeriod.endDate = now
            set_award_contracts_cancelled(self.request, award)
            add_next_award(self.request)
        elif award_status == "pending" and award.status == "unsuccessful":
            if not new_defence_complaints:
                award.complaintPeriod = {
                    "startDate": now.isoformat(),
                    "endDate": calculate_complaint_business_date(now, STAND_STILL_TIME, tender, True)
                }
            add_next_award(self.request)
        elif (
            award_status == "unsuccessful"
            and award.status == "cancelled"
            and any([i.status == "satisfied" for i in award.complaints])
        ):
            if tender.status == "active.awarded":
                tender.status = "active.qualification"
                tender.awardPeriod.endDate = None
            if (
                not new_defence_complaints
                and award.complaintPeriod.endDate > now
            ):
                award.complaintPeriod.endDate = now
            for i in tender.awards:
                if i.lotID != award.lotID:
                    continue
                if (
                    not new_defence_complaints
                    and i.complaintPeriod
                    and (not i.complaintPeriod.endDate or i.complaintPeriod.endDate > now)
                ):
                    i.complaintPeriod.endDate = now
                i.status = "cancelled"
                set_award_contracts_cancelled(self.request, i)
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
