# -*- coding: utf-8 -*-
from datetime import timedelta, datetime, time
from schematics.exceptions import ValidationError
from schematics.types import StringType, BooleanType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from zope.interface import implementer
from openprocurement.api.utils import get_now
from openprocurement.api.models import (
    Period,
    ListType,
    ContactPoint as BaseContactPoint,
    SifterListType,
)
from openprocurement.tender.core.models import (
    ProcuringEntity as BaseProcuringEntity,
    EnquiryPeriod,
    LotWithMinimalStepLimitsValidation as BaseLot,
    validate_lots_uniq,
    get_tender,
)
from openprocurement.tender.openua.models import (
    Tender as BaseTender,
    Cancellation as BaseCancellation,
    IAboveThresholdUATender,
    BaseUaBid,
)
from openprocurement.tender.core.utils import (
    calc_auction_end_time,
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
from openprocurement.tender.openuadefense.validation import validate_tender_period_duration


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

    def validate_tenderPeriod(self, data, period):
        if period:
            validate_tender_period_duration(data, period, TENDERING_DURATION, working_days=True)

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
