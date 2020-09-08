# -*- coding: utf-8 -*-
from openprocurement.api.utils import\
    get_now, json_view, context_unpack, raise_operation_error
from openprocurement.tender.core.utils import\
    optendersresource, save_tender, apply_patch
from openprocurement.tender.belowthreshold.views.award import\
    TenderAwardResource
from openprocurement.tender.pricequotation.utils import\
    add_next_award, add_contract
from openprocurement.tender.pricequotation.constants import PMT
from openprocurement.tender.core.validation import (
    validate_award_data,
    validate_patch_award_data,
    validate_update_award_in_not_allowed_status,
)
from openprocurement.tender.pricequotation.validation import (
    validate_create_award_not_in_allowed_period,
    validate_award_update_in_terminal_status,
)


@optendersresource(
    name="{}:Tender Awards".format(PMT),
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType=PMT,
)
class PQTenderAwardResource(TenderAwardResource):
    """ PriceQuotation award resource """
    @json_view(
        content_type="application/json",
        permission="create_award",
        validators=(
            validate_award_data,
            validate_create_award_not_in_allowed_period,
        ),
    )
    def collection_post(self):
        tender = self.request.validated["tender"]
        award = self.request.validated["award"]
        tender.awards.append(award)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender award {}".format(award.id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_award_create"},
                    {"award_id": award.id}
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Awards".format(tender.procurementMethodType),
                tender_id=tender.id, award_id=award["id"]
            )

            return {"data": award.serialize("view")}

    @json_view(
        content_type="application/json",
        permission="edit_award",
        validators=(
            validate_patch_award_data,
            validate_update_award_in_not_allowed_status,
            validate_award_update_in_terminal_status
        ),
    )
    def patch(self):
        tender = self.request.validated["tender"]
        award = self.request.context
        is_awarded = [
            a for a in tender.awards
            if a.bid_id == award.bid_id and a.id != award.id
        ]
        award_status = award.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())

        now = get_now()
        if is_awarded and award_status == 'pending' and award.status not in ('unsuccessful'):
            raise_operation_error(
                self.request,
                "Can't change award status to ({})".format(award.status)
            )

        if award_status == "pending" and award.status == "active":
            add_contract(self.request, award, now)
            add_next_award(self.request)
        elif award_status == "active" and award.status == "cancelled":
            for i in tender.contracts:
                if i.awardID == award.id:
                    i.status = "cancelled"
            add_next_award(self.request)
        elif award_status == "pending" and award.status == "unsuccessful":
            if is_awarded:
                tender.status = 'unsuccessful'
            else:
                add_next_award(self.request)
        elif (
            award_status == "unsuccessful"
            and award.status == "cancelled"
        ):
            if tender.status == "active.awarded":
                tender.status = "active.qualification"
                tender.awardPeriod.endDate = None
            cancelled_awards = []
            for i in tender.awards[tender.awards.index(award):]:
                i.status = "cancelled"
                cancelled_awards.append(i.id)
            for i in tender.contracts:
                if i.awardID in cancelled_awards:
                    i.status = "cancelled"
            add_next_award(self.request)
        elif self.request.authenticated_role != "Administrator" and not (
            award_status == "pending" and award.status == "pending"
        ):
            raise_operation_error(
                self.request,
                "Can't update award in current ({}) status".format(award_status)
            )
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender award {}".format(self.request.context.id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_award_patch"}
                ),
            )
            return {"data": award.serialize("view")}
