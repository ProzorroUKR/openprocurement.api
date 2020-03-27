# -*- coding: utf-8 -*-
from openprocurement.api.utils import context_unpack, get_now, json_view, raise_operation_error
from openprocurement.tender.core.validation import (
    validate_patch_award_data,
    validate_update_award_only_for_active_lots,
    validate_update_award_with_accepted_complaint,
    validate_operation_with_lot_cancellation_in_pending,
)
from openprocurement.tender.core.utils import apply_patch, optendersresource, save_tender
from openprocurement.tender.openua.views.award import TenderUaAwardResource as BaseResource
from openprocurement.tender.cfaua.utils import add_next_awards
from openprocurement.tender.cfaua.validation import validate_update_award_in_not_allowed_status


@optendersresource(
    name="closeFrameworkAgreementUA:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender EU awards",
    procurementMethodType="closeFrameworkAgreementUA",
)
class TenderAwardResource(BaseResource):
    """ EU award resource """

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_patch_award_data,
            validate_operation_with_lot_cancellation_in_pending("award"),
            validate_update_award_in_not_allowed_status,
            validate_update_award_only_for_active_lots,
            validate_update_award_with_accepted_complaint,
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
        configurator = self.request.content_configurator

        now = get_now()

        if award_status != award.status and award.status == "unsuccessful":
            if award.complaintPeriod:
                award.complaintPeriod.startDate = now
            else:
                award.complaintPeriod = {"startDate": now.isoformat()}
        if (
            tender.status == "active.qualification.stand-still"
            and award_status == "active"
            and award.status == "cancelled"
        ):
            for aw in tender.awards:
                if aw.lotID == award.lotID:
                    aw.status = "cancelled"
            add_next_awards(
                self.request,
                reverse=configurator.reverse_awarding_criteria,
                awarding_criteria_key=configurator.awarding_criteria_key,
                regenerate_all_awards=True,
                lot_id=award.lotID,
            )
            self.context.dateDecision = now
            tender.status = "active.qualification"
            if tender.awardPeriod.endDate:
                tender.awardPeriod.endDate = None
        else:
            if award_status == "pending" and award.status == "unsuccessful":
                add_next_awards(
                    self.request,
                    reverse=configurator.reverse_awarding_criteria,
                    awarding_criteria_key=configurator.awarding_criteria_key,
                )
            elif award_status == "pending" and award.status == "active":
                pass
            elif award_status == "active" and award.status == "cancelled":
                add_next_awards(
                    self.request,
                    reverse=configurator.reverse_awarding_criteria,
                    awarding_criteria_key=configurator.awarding_criteria_key,
                    lot_id=award.lotID,
                )
            elif award_status == "unsuccessful" and award.status == "cancelled":
                for aw in tender.awards:
                    if aw.lotID == award.lotID:
                        aw.status = "cancelled"
                add_next_awards(
                    self.request,
                    reverse=configurator.reverse_awarding_criteria,
                    awarding_criteria_key=configurator.awarding_criteria_key,
                    regenerate_all_awards=True,
                    lot_id=award.lotID,
                )
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
