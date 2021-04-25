# -*- coding: utf-8 -*-
from datetime import timedelta, datetime, time
from schematics.exceptions import ValidationError
from schematics.types import StringType, BooleanType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from zope.interface import implementer
from openprocurement.api.utils import get_now, get_first_revision_date
from openprocurement.api.models import (
    Period,
    ListType,
    ContactPoint as BaseContactPoint,
    SifterListType,
)
from openprocurement.api.constants import (
    TZ,
    NEW_DEFENSE_COMPLAINTS_FROM,
    NEW_DEFENSE_COMPLAINTS_TO,
)
from openprocurement.tender.core.models import (
    ProcuringEntity as BaseProcuringEntity,
    EnquiryPeriod,
    LotWithMinimalStepLimitsValidation as BaseLot,
    validate_lots_uniq,
    get_tender,
)
from openprocurement.tender.core.constants import AWARD_CRITERIA_LOWEST_COST
from openprocurement.tender.openua.models import (
    Tender as BaseTender,
    Cancellation as BaseCancellation,
    IAboveThresholdUATender,
    BaseUaBid,
)
from openprocurement.tender.core.utils import (
    calc_auction_end_time,
    has_unanswered_questions,
    has_unanswered_complaints,
    extend_next_check_by_complaint_period_ends,
    cancellation_block_tender,
)
from openprocurement.tender.openuadefense.constants import (
    TENDERING_DURATION,
    ENQUIRY_STAND_STILL_TIME,
    ENQUIRY_PERIOD_TIME,
    COMPLAINT_SUBMIT_TIME,
    COMPLAINT_OLD_SUBMIT_TIME,
    COMPLAINT_OLD_SUBMIT_TIME_BEFORE,
)
from openprocurement.tender.openuadefense.utils import (
    calculate_tender_business_date,
    calculate_clarif_business_date,
    calculate_complaint_business_date,
)
from openprocurement.tender.openuadefense.validation import _validate_tender_period_duration


class IAboveThresholdUADefTender(IAboveThresholdUATender):
    """ Marker interface for aboveThresholdUA defense tenders """


class LotAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        tender = get_tender(self)
        lot = self.__parent__
        statuses = ["active.tendering", "active.auction"]
        if tender.status not in statuses or lot.status != "active":
            return
        if tender.status == "active.auction" and lot.numberOfBids < 2:
            return
        if self.startDate and get_now() > calc_auction_end_time(lot.numberOfBids, self.startDate):
            return calc_auction_end_time(lot.numberOfBids, self.startDate).isoformat()
        else:
            decision_dates = [
                datetime.combine(
                    complaint.dateDecision.date() + timedelta(days=3), time(0, tzinfo=complaint.dateDecision.tzinfo)
                )
                for complaint in tender.complaints
                if complaint.dateDecision
            ]
            decision_dates.append(tender.tenderPeriod.endDate)
            return max(decision_dates).isoformat()


class Lot(BaseLot):

    auctionPeriod = ModelType(LotAuctionPeriod, default={})


class ContactPoint(BaseContactPoint):

    availableLanguage = StringType(choices=["uk", "en", "ru"])


class ProcuringEntity(BaseProcuringEntity):

    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True), required=False)


class Cancellation(BaseCancellation):
    class Options:
        roles = BaseCancellation._options.roles

    _after_release_reasonType_choices = ["noDemand", "unFixable", "expensesCut"]


class Bid(BaseUaBid):
    selfEligible = BooleanType(choices=[True], required=True)


@implementer(IAboveThresholdUADefTender)
class Tender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""

    awardCriteria = StringType(
        choices=[AWARD_CRITERIA_LOWEST_COST],
        default=AWARD_CRITERIA_LOWEST_COST
    )
    procuringEntity = ModelType(
        ProcuringEntity, required=True
    )  # The entity managing the procurement, which may be different from the buyer who is paying / using the items
    lots = ListType(ModelType(Lot, required=True), default=list(), validators=[validate_lots_uniq])
    procurementMethodType = StringType(default="aboveThresholdUA.defense")
    procuring_entity_kinds = ["defense"]

    bids = SifterListType(
        ModelType(Bid, required=True), default=list(), filter_by="status", filter_in_values=["invalid", "deleted"]
    )

    cancellations = ListType(ModelType(Cancellation, required=True), default=list())

    def validate_awardCriteria(self, data, value):
        # for deactivate validation of awardCriteria from parent class
        return

    def validate_tenderPeriod(self, data, period):
        if period:
            _validate_tender_period_duration(data, period, TENDERING_DURATION, working_days=True)

    @serializable(serialized_name="enquiryPeriod", type=ModelType(EnquiryPeriod))
    def tender_enquiryPeriod(self):
        end_date = calculate_tender_business_date(self.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME, self, True)
        clarifications_until = calculate_clarif_business_date(end_date, ENQUIRY_STAND_STILL_TIME, self, True)
        return EnquiryPeriod(
            dict(
                startDate=self.tenderPeriod.startDate,
                endDate=end_date,
                invalidationDate=self.enquiryPeriod and self.enquiryPeriod.invalidationDate,
                clarificationsUntil=clarifications_until,
            )
        )

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        if self.tenderPeriod.startDate < COMPLAINT_OLD_SUBMIT_TIME_BEFORE:
            end_date = calculate_tender_business_date(self.tenderPeriod.endDate, -COMPLAINT_OLD_SUBMIT_TIME, self)
        else:
            end_date = calculate_complaint_business_date(self.tenderPeriod.endDate, -COMPLAINT_SUBMIT_TIME, self, True)
        return Period(dict(startDate=self.tenderPeriod.startDate, endDate=end_date))

    def validate_criteria(self, data, value):
        if value:
            raise ValidationError("Rogue field")

    @serializable(serialize_when_none=False)
    def next_check(self):
        now = get_now()
        checks = []

        extend_next_check_by_complaint_period_ends(self, checks)

        if cancellation_block_tender(self):
            return min(checks).isoformat() if checks else None

        if (
            self.status == "active.tendering"
            and self.tenderPeriod.endDate
            and not has_unanswered_complaints(self)
            and not has_unanswered_questions(self)
        ):
            checks.append(self.tenderPeriod.endDate.astimezone(TZ))
        elif (
            not self.lots
            and self.status == "active.auction"
            and self.auctionPeriod
            and self.auctionPeriod.startDate
            and not self.auctionPeriod.endDate
        ):
            if now < self.auctionPeriod.startDate:
                checks.append(self.auctionPeriod.startDate.astimezone(TZ))
            else:
                auction_end_time = calc_auction_end_time(
                    self.numberOfBids, self.auctionPeriod.startDate
                ).astimezone(TZ)
                if now < auction_end_time:
                    checks.append(auction_end_time)
        elif self.lots and self.status == "active.auction":
            for lot in self.lots:
                if (
                    lot.status != "active"
                    or not lot.auctionPeriod
                    or not lot.auctionPeriod.startDate
                    or lot.auctionPeriod.endDate
                ):
                    continue
                if now < lot.auctionPeriod.startDate:
                    checks.append(lot.auctionPeriod.startDate.astimezone(TZ))
                else:
                    auction_end_time = calc_auction_end_time(
                        lot.numberOfBids, lot.auctionPeriod.startDate
                    ).astimezone(TZ)
                    if now < auction_end_time:
                        checks.append(auction_end_time)
        elif (
            not self.lots
            and self.status == "active.awarded"
            and not any([i.status in self.block_complaint_status for i in self.complaints])
            and not any([i.status in self.block_complaint_status for a in self.awards for i in a.complaints])
        ):
            first_revision_date = get_first_revision_date(self)
            new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < first_revision_date < NEW_DEFENSE_COMPLAINTS_TO
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in self.awards
                if (
                    a.complaintPeriod
                    and a.complaintPeriod.endDate
                    and (a.status != "cancelled" if new_defence_complaints else True)
                )
            ]
            last_award_status = self.awards[-1].status if self.awards else ""
            if standStillEnds and last_award_status == "unsuccessful":
                checks.append(max(standStillEnds))
        elif (
            self.lots
            and self.status in ["active.qualification", "active.awarded"]
            and not any([i.status in self.block_complaint_status and i.relatedLot is None for i in self.complaints])
        ):
            for lot in self.lots:
                if lot["status"] != "active":
                    continue
                lot_awards = [i for i in self.awards if i.lotID == lot.id]
                pending_complaints = any(
                    [i["status"] in self.block_complaint_status and i.relatedLot == lot.id for i in self.complaints]
                )
                pending_awards_complaints = any(
                    [i.status in self.block_complaint_status for a in lot_awards for i in a.complaints]
                )
                first_revision_date = get_first_revision_date(self)
                new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < first_revision_date < NEW_DEFENSE_COMPLAINTS_TO
                standStillEnds = [
                    a.complaintPeriod.endDate.astimezone(TZ)
                    for a in lot_awards
                    if (
                            a.complaintPeriod
                            and a.complaintPeriod.endDate
                            and (a.status != "cancelled" if new_defence_complaints else True)
                    )
                ]
                last_award_status = lot_awards[-1].status if lot_awards else ""
                if (
                    not pending_complaints
                    and not pending_awards_complaints
                    and standStillEnds
                    and last_award_status == "unsuccessful"
                ):
                    checks.append(max(standStillEnds))
        if self.status.startswith("active"):
            for award in self.awards:
                if award.status == "active" and not any([i.awardID == award.id for i in self.contracts]):
                    checks.append(award.date)

        return min(checks).isoformat() if checks else None
