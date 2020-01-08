# -*- coding: utf-8 -*-
from datetime import time, timedelta, datetime
from iso8601 import parse_date
from zope.interface import implementer
from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist, blacklist
from schematics.types import StringType, BooleanType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from openprocurement.api.utils import get_now, get_first_revision_date
from openprocurement.api.models import (
    schematics_default_role,
    schematics_embedded_role,
    Model,
    PeriodEndRequired as BasePeriodEndRequired,
    ListType,
    SifterListType,
    Period,
    IsoDateTimeType,
    Address,
)
from openprocurement.api.constants import TZ
from openprocurement.api.auth import ACCR_3, ACCR_4, ACCR_5
from openprocurement.api.validation import validate_cpv_group, validate_items_uniq, validate_classification_id
from openprocurement.tender.core.models import (
    view_bid_role,
    Administrator_bid_role,
    get_tender,
    validate_lots_uniq,
    bids_validation_wrapper,
    Lot,
    ComplaintModelType,
    Award as BaseAward,
    Parameter as BaseParameter,
    Bid as BaseBid,
    Complaint as BaseComplaint,
    LotValue as BaseLotValue,
    Item as BaseItem,
    Contract as BaseContract,
    Cancellation,
    validate_parameters_uniq,
    ITender,
    PeriodStartEndRequired,
    EnquiryPeriod,
    ConfidentialDocument,
)
from openprocurement.tender.core.utils import (
    rounding_shouldStartAfter,
    has_unanswered_questions,
    has_unanswered_complaints,
    calc_auction_end_time,
    calculate_tender_business_date,
    calculate_complaint_business_date,
    calculate_clarifications_business_date,
)
from openprocurement.tender.core.validation import validate_lotvalue_value, validate_relatedlot
from openprocurement.tender.belowthreshold.models import Tender as BaseTender
from openprocurement.tender.openua.constants import (
    ENQUIRY_STAND_STILL_TIME,
    COMPLAINT_SUBMIT_TIME,
    TENDER_PERIOD,
    ENQUIRY_PERIOD_TIME,
    AUCTION_PERIOD_TIME,
    PERIOD_END_REQUIRED_FROM,
)

class IAboveThresholdUATender(ITender):
    """ Marker interface for aboveThresholdUA tenders """


class TenderAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        tender = self.__parent__
        if tender.lots or tender.status not in ["active.tendering", "active.auction"]:
            return
        if self.startDate and get_now() > calc_auction_end_time(tender.numberOfBids, self.startDate):
            start_after = calc_auction_end_time(tender.numberOfBids, self.startDate)
        else:
            decision_dates = [
                datetime.combine(
                    complaint.dateDecision.date() + timedelta(days=3), time(0, tzinfo=complaint.dateDecision.tzinfo)
                )
                for complaint in tender.complaints
                if complaint.dateDecision
            ]
            decision_dates.append(tender.tenderPeriod.endDate)
            start_after = max(decision_dates)
        return rounding_shouldStartAfter(start_after, tender).isoformat()


class PeriodEndRequired(BasePeriodEndRequired):
    # TODO different validator compared with belowthreshold
    def validate_startDate(self, data, value):
        tender = get_tender(data["__parent__"])
        tender_date = get_first_revision_date(tender, default=get_now())
        if tender_date < PERIOD_END_REQUIRED_FROM:
            return
        if value and data.get("endDate") and data.get("endDate") < value:
            raise ValidationError(u"period should begin before its end")


class Item(BaseItem):
    """A good, service, or work to be contracted."""

    deliveryDate = ModelType(PeriodEndRequired, required=True)
    deliveryAddress = ModelType(Address, required=True)


class Contract(BaseContract):

    items = ListType(ModelType(Item, required=True))


class LotValue(BaseLotValue):
    class Options:
        roles = {
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
            "create": whitelist("value", "relatedLot", "subcontractingDetails"),
            "edit": whitelist("value", "relatedLot", "subcontractingDetails"),
            "auction_view": whitelist("value", "date", "relatedLot", "participationUrl"),
            "auction_post": whitelist("value", "date", "relatedLot"),
            "auction_patch": whitelist("participationUrl", "relatedLot"),
        }

    subcontractingDetails = StringType()

    skip = ("invalid", "deleted", "draft")

    def validate_value(self, data, value):
        parent = data["__parent__"]
        if isinstance(parent, Bid) and parent.status not in self.skip:
            validate_lotvalue_value(get_tender(parent), data["relatedLot"], value)

    def validate_relatedLot(self, data, relatedLot):
        parent = data["__parent__"]
        if isinstance(parent, Model) and parent.status not in self.skip:
            validate_relatedlot(get_tender(parent), relatedLot)


class Parameter(BaseParameter):
    @bids_validation_wrapper
    def validate_value(self, data, value):
        BaseParameter._validator_functions["value"](self, data, value)

    @bids_validation_wrapper
    def validate_code(self, data, code):
        BaseParameter._validator_functions["code"](self, data, code)


class Bid(BaseBid):
    class Options:
        roles = {
            "Administrator": Administrator_bid_role,
            "embedded": view_bid_role,
            "view": view_bid_role,
            "create": whitelist(
                "value",
                "tenderers",
                "parameters",
                "lotValues",
                "status",
                "selfQualified",
                "selfEligible",
                "subcontractingDetails",
                "documents",
            ),
            "edit": whitelist("value", "tenderers", "parameters", "lotValues", "status", "subcontractingDetails"),
            "auction_view": whitelist("value", "lotValues", "id", "date", "parameters", "participationUrl", "status"),
            "auction_post": whitelist("value", "lotValues", "id", "date"),
            "auction_patch": whitelist("id", "lotValues", "participationUrl"),
            "active.enquiries": whitelist(),
            "active.tendering": whitelist(),
            "active.auction": whitelist(),
            "active.qualification": view_bid_role,
            "active.awarded": view_bid_role,
            "complete": view_bid_role,
            "unsuccessful": view_bid_role,
            "cancelled": view_bid_role,
            "invalid": whitelist("id", "status"),
            "deleted": whitelist("id", "status"),
        }

    lotValues = ListType(ModelType(LotValue, required=True), default=list())
    subcontractingDetails = StringType()
    status = StringType(choices=["draft", "active", "invalid", "deleted"], default="active")
    selfQualified = BooleanType(required=True, choices=[True])
    selfEligible = BooleanType(required=True, choices=[True])
    parameters = ListType(ModelType(Parameter, required=True), default=list(), validators=[validate_parameters_uniq])
    documents = ListType(ModelType(ConfidentialDocument, required=True), default=list())

    def serialize(self, role=None):
        if role and self.status in ["invalid", "deleted"]:
            role = self.status
        return super(Bid, self).serialize(role)

    @bids_validation_wrapper
    def validate_value(self, data, value):
        BaseBid._validator_functions["value"](self, data, value)

    @bids_validation_wrapper
    def validate_lotValues(self, data, lotValues):
        BaseBid._validator_functions["lotValues"](self, data, lotValues)

    @bids_validation_wrapper
    def validate_participationUrl(self, data, participationUrl):
        BaseBid._validator_functions["participationUrl"](self, data, participationUrl)

    @bids_validation_wrapper
    def validate_parameters(self, data, parameters):
        BaseBid._validator_functions["parameters"](self, data, parameters)


class Complaint(BaseComplaint):
    class Options:
        roles = {
            "create": whitelist("author", "title", "description", "status", "relatedLot"),
            "draft": whitelist("author", "title", "description", "status"),
            "cancellation": whitelist("cancellationReason", "status"),
            "satisfy": whitelist("satisfied", "status"),
            "escalate": whitelist("status"),
            "resolve": whitelist("status", "tendererAction"),
            "answer": whitelist("resolution", "resolutionType", "status", "tendererAction"),
            "action": whitelist("tendererAction"),
            "pending": whitelist("decision", "status", "rejectReason", "rejectReasonDescription"),
            "review": whitelist("decision", "status", "reviewDate", "reviewPlace"),
            "embedded": (blacklist("owner_token", "owner", "transfer_token", "bid_id") + schematics_embedded_role),
            "view": (blacklist("owner_token", "owner", "transfer_token", "bid_id") + schematics_default_role),
        }

    status = StringType(
        choices=[
            "draft",
            "claim",
            "answered",
            "pending",
            "accepted",
            "invalid",
            "resolved",
            "declined",
            "cancelled",
            "satisfied",
            "stopping",
            "stopped",
            "mistaken",
        ],
        default="draft",
    )
    acceptance = BooleanType()
    dateAccepted = IsoDateTimeType()
    rejectReason = StringType(choices=["lawNonСompliance", "noPaymentReceived", "buyerViolationsСorrected"])
    rejectReasonDescription = StringType()
    reviewDate = IsoDateTimeType()
    reviewPlace = StringType()
    bid_id = StringType()

    def __acl__(self):
        return [
            (Allow, "g:aboveThresholdReviewers", "edit_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_complaint_documents"),
        ]

    def get_role(self):
        root = self.get_root()
        request = root.request
        data = request.json_body["data"]
        if request.authenticated_role == "complaint_owner" and data.get("status", self.status) == "cancelled":
            role = "cancellation"
        elif (
            request.authenticated_role == "complaint_owner"
            and self.status in ["pending", "accepted"]
            and data.get("status", self.status) == "stopping"
        ):
            role = "cancellation"
        elif request.authenticated_role == "complaint_owner" and self.status == "draft":
            role = "draft"
        elif request.authenticated_role == "complaint_owner" and self.status == "claim":
            role = "escalate"
        elif request.authenticated_role == "tender_owner" and self.status == "claim":
            role = "answer"
        elif request.authenticated_role == "tender_owner" and self.status in ["pending", "accepted"]:
            role = "action"
        elif request.authenticated_role == "tender_owner" and self.status == "satisfied":
            role = "resolve"
        elif request.authenticated_role == "complaint_owner" and self.status == "answered":
            role = "satisfy"
        elif request.authenticated_role == "aboveThresholdReviewers" and self.status == "pending":
            role = "pending"
        elif request.authenticated_role == "aboveThresholdReviewers" and self.status in ["accepted", "stopping"]:
            role = "review"
        else:
            role = "invalid"
        return role

    def validate_cancellationReason(self, data, cancellationReason):
        if not cancellationReason and data.get("status") in ["cancelled", "stopping"]:
            raise ValidationError(u"This field is required.")


class Award(BaseAward):
    class Options:
        roles = {
            "edit": whitelist(
                "status",
                "qualified",
                "eligible",
                "title",
                "title_en",
                "title_ru",
                "description",
                "description_en",
                "description_ru",
            )
        }

    complaints = ListType(ModelType(Complaint, required=True), default=list())
    items = ListType(ModelType(Item, required=True))
    qualified = BooleanType(default=False)
    eligible = BooleanType(default=False)

    def validate_qualified(self, data, qualified):
        if data["status"] == "active" and not qualified:
            raise ValidationError(u"This field is required.")

    def validate_eligible(self, data, eligible):
        if data["status"] == "active" and not eligible:
            raise ValidationError(u"This field is required.")


@implementer(IAboveThresholdUATender)
class Tender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""

    class Options:
        namespace = "Tender"
        _parent_roles = BaseTender.Options.roles

        _edit_role = _parent_roles["edit"]
        _above_fields = whitelist("complaintPeriod")
        _tendering_role = _parent_roles["active.tendering"] + _above_fields
        _view_role = _parent_roles["view"] + _above_fields
        _all_forbidden = whitelist()
        roles = {
            "create": _parent_roles["create"],
            "edit_draft": _parent_roles["edit_draft"],
            "edit": _edit_role,
            "edit_active.tendering": _edit_role,
            "edit_active.auction": _all_forbidden,
            "edit_active.qualification": _all_forbidden,
            "edit_active.awarded": _all_forbidden,
            "edit_complete": _all_forbidden,
            "edit_unsuccessful": _all_forbidden,
            "edit_cancelled": _all_forbidden,
            "draft": _tendering_role,
            "active.tendering": _tendering_role,
            "active.auction": _tendering_role,
            "view": _view_role,
            "active.qualification": _view_role,
            "active.awarded": _view_role,
            "complete": _view_role,
            "unsuccessful": _view_role,
            "cancelled": _view_role,
            "chronograph": _parent_roles["chronograph"],
            "chronograph_view": _parent_roles["chronograph_view"],
            "Administrator": _parent_roles["Administrator"],
            "default": _parent_roles["default"],
            "plain": _parent_roles["plain"],
            "listing": _parent_roles["listing"],
            "auction_view": _parent_roles["auction_view"],
            "auction_post": _parent_roles["auction_post"],
            "auction_patch": _parent_roles["auction_patch"],
            "contracting": _parent_roles["contracting"],
        }

    __name__ = ""

    enquiryPeriod = ModelType(EnquiryPeriod, required=False)
    tenderPeriod = ModelType(PeriodStartEndRequired, required=True)
    auctionPeriod = ModelType(TenderAuctionPeriod, default={})
    bids = SifterListType(
        ModelType(Bid, required=True), default=list(), filter_by="status", filter_in_values=["invalid", "deleted"]
    )  # A list of all the companies who entered submissions for the tender.
    awards = ListType(ModelType(Award, required=True), default=list())
    contracts = ListType(ModelType(Contract, required=True), default=list())
    complaints = ListType(ComplaintModelType(Complaint, required=True), default=list())
    procurementMethodType = StringType(default="aboveThresholdUA")
    lots = ListType(ModelType(Lot, required=True), default=list(), validators=[validate_lots_uniq])
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.auction",
            "active.qualification",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
        ],
        default="active.tendering",
    )
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
    )  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    cancellations = ListType(ModelType(Cancellation, required=True), default=list())

    create_accreditations = (ACCR_3, ACCR_5)
    central_accreditations = (ACCR_5,)
    edit_accreditations = (ACCR_4,)

    procuring_entity_kinds = ["general", "special", "defense", "central"]
    block_tender_complaint_status = ["claim", "pending", "accepted", "satisfied", "stopping"]
    block_complaint_status = ["pending", "accepted", "satisfied", "stopping"]

    def __acl__(self):
        acl = [
            (Allow, "{}_{}".format(i.owner, i.owner_token), "create_award_complaint")
            for i in self.bids
            if i.status == "active"
        ]
        acl.extend(
            [
                (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_complaint"),
            ]
        )

        self._acl_cancellation_complaint(acl)
        return acl

    def validate_enquiryPeriod(self, data, period):
        # for deactivate validation to enquiryPeriod from parent tender
        return

    def validate_tenderPeriod(self, data, period):
        # data['_rev'] is None when tender was created just now
        if not data["_rev"] and calculate_tender_business_date(get_now(), -timedelta(minutes=10)) >= period.startDate:
            raise ValidationError(u"tenderPeriod.startDate should be in greater than current date")
        if period and calculate_tender_business_date(period.startDate, TENDER_PERIOD, data) > period.endDate:
            raise ValidationError(u"tenderPeriod should be greater than 15 days")

    @serializable(serialized_name="enquiryPeriod", type=ModelType(EnquiryPeriod))
    def tender_enquiryPeriod(self):
        endDate = calculate_tender_business_date(self.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME, self)
        clarificationsUntil = calculate_clarifications_business_date(endDate, ENQUIRY_STAND_STILL_TIME, self, True)
        return EnquiryPeriod(
            dict(
                startDate=self.tenderPeriod.startDate,
                endDate=endDate,
                invalidationDate=self.enquiryPeriod and self.enquiryPeriod.invalidationDate,
                clarificationsUntil=clarificationsUntil,
            )
        )

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        endDate = calculate_complaint_business_date(self.tenderPeriod.endDate, -COMPLAINT_SUBMIT_TIME, self)
        return Period(dict(startDate=self.tenderPeriod.startDate, endDate=endDate))

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        return len([bid for bid in self.bids if bid.status == "active"])

    @serializable(serialize_when_none=False)
    def next_check(self):
        now = get_now()
        checks = []
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
            elif now < calc_auction_end_time(self.numberOfBids, self.auctionPeriod.startDate).astimezone(TZ):
                checks.append(calc_auction_end_time(self.numberOfBids, self.auctionPeriod.startDate).astimezone(TZ))
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
                elif now < calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(TZ):
                    checks.append(calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(TZ))
        elif (
            not self.lots
            and self.status == "active.awarded"
            and not any([i.status in self.block_complaint_status for i in self.complaints])
            and not any([i.status in self.block_complaint_status for a in self.awards for i in a.complaints])
        ):
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ) for a in self.awards if a.complaintPeriod.endDate
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
                standStillEnds = [
                    a.complaintPeriod.endDate.astimezone(TZ) for a in lot_awards if a.complaintPeriod.endDate
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
        if (
            self.cancellations
            and self.cancellations[-1].status == "pending"
            and self.cancellations[-1].complaintPeriod
        ):
            cancellation = self.cancellations[-1]
            checks.append(cancellation.complaintPeriod.endDate.astimezone(TZ))
        return min(checks).isoformat() if checks else None

    def invalidate_bids_data(self):
        if (
            self.auctionPeriod
            and self.auctionPeriod.startDate
            and self.auctionPeriod.shouldStartAfter
            and self.auctionPeriod.startDate
            > calculate_tender_business_date(
                parse_date(self.auctionPeriod.shouldStartAfter), AUCTION_PERIOD_TIME, self, True
            )
        ):
            self.auctionPeriod.startDate = None
        for lot in self.lots:
            if (
                lot.auctionPeriod
                and lot.auctionPeriod.startDate
                and lot.auctionPeriod.shouldStartAfter
                and lot.auctionPeriod.startDate
                > calculate_tender_business_date(
                    parse_date(lot.auctionPeriod.shouldStartAfter), AUCTION_PERIOD_TIME, self, True
                )
            ):
                lot.auctionPeriod.startDate = None
        self.enquiryPeriod.invalidationDate = get_now()
        for bid in self.bids:
            if bid.status not in ["deleted", "draft"]:
                bid.status = "invalid"
