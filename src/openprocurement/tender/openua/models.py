# -*- coding: utf-8 -*-
from uuid import uuid4

from datetime import time, timedelta, datetime
from zope.interface import implementer
from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist, blacklist
from schematics.types import StringType, BooleanType, MD5Type, BaseType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from openprocurement.api.utils import get_now, get_first_revision_date, is_new_created
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
from openprocurement.api.constants import TZ, RELEASE_2020_04_19
from openprocurement.api.auth import ACCR_3, ACCR_4, ACCR_5
from openprocurement.api.validation import validate_cpv_group, validate_items_uniq, validate_classification_id
from openprocurement.tender.core.models import (
    view_bid_role,
    Administrator_bid_role,
    get_tender,
    validate_lots_uniq,
    bids_validation_wrapper,
    LotWithMinimalStepLimitsValidation as Lot,
    ComplaintModelType,
    Award as BaseAward,
    Parameter as BaseParameter,
    Bid as BaseBid,
    Complaint as BaseComplaint,
    LotValue as BaseLotValue,
    Item as BaseItem,
    Contract as BaseContract,
    Cancellation as BaseCancellation,
    validate_parameters_uniq,
    ITender,
    PeriodStartEndRequired,
    EnquiryPeriod,
    ConfidentialDocumentModelType,
    ConfidentialDocument,
    Document,
    QualificationMilestoneListMixin,
)
from openprocurement.tender.core.utils import (
    normalize_should_start_after,
    has_unanswered_questions,
    has_unanswered_complaints,
    calc_auction_end_time,
    calculate_tender_business_date,
    calculate_complaint_business_date,
    calculate_clarif_business_date,
    check_auction_period,
    extend_next_check_by_complaint_period_ends,
)
from openprocurement.tender.core.validation import (
    validate_lotvalue_value,
    validate_relatedlot,
    ValidateSelfEligibleMixin,
)
from openprocurement.tender.belowthreshold.models import Tender as BaseTender
from openprocurement.tender.openua.constants import (
    ENQUIRY_STAND_STILL_TIME,
    COMPLAINT_SUBMIT_TIME,
    TENDERING_DURATION,
    ENQUIRY_PERIOD_TIME,
    PERIOD_END_REQUIRED_FROM,
)
from openprocurement.tender.openua.validation import (
    validate_tender_period_duration,
    validate_tender_period_start_date,
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
        return normalize_should_start_after(start_after, tender).isoformat()


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
        if isinstance(parent, BaseUaBid) and parent.status not in self.skip:
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


class BaseUaBid(BaseBid):
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
    selfEligible = BooleanType(choices=[True])
    parameters = ListType(ModelType(Parameter, required=True), default=list(), validators=[validate_parameters_uniq])
    documents = ListType(ConfidentialDocumentModelType(ConfidentialDocument, required=True), default=list())

    def serialize(self, role=None):
        if role and self.status in ["invalid", "deleted"]:
            role = self.status
        return super(BaseUaBid, self).serialize(role)

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


class Bid(BaseUaBid, ValidateSelfEligibleMixin):
    pass


class ComplaintPost(Model):
    class Options:
        namespace = "post"
        roles = {
            "create": whitelist("title", "description", "documents", "relatedParty", "relatedPost", "recipient"),
            "edit": whitelist(),
            "view": schematics_default_role,
            "default": schematics_default_role,
            "embedded": schematics_embedded_role,
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)

    title = StringType(required=True)
    description = StringType(required=True)
    documents = ListType(ModelType(Document), default=list())
    author = StringType(choices=["complaint_owner", "tender_owner", "aboveThresholdReviewers"])
    recipient = StringType(required=True, choices=["complaint_owner", "tender_owner", "aboveThresholdReviewers"])
    datePublished = IsoDateTimeType(default=get_now)
    relatedPost = StringType()

    reviewer_roles = ["aboveThresholdReviewers"]
    recipient_roles = ["complaint_owner", "tender_owner"]

    def validate_relatedPost(self, data, value):
        parent = data["__parent__"]

        if data["author"] in self.recipient_roles and not value:
            raise ValidationError(BaseType.MESSAGES["required"])

        if value and isinstance(parent, Model):

            # check that another post with "id"
            # that equals "relatedPost" of current post exists
            if value not in [i.id for i in parent.posts]:
                raise ValidationError("relatedPost should be one of posts.")

            # check that another posts with `relatedPost`
            # that equals `relatedPost` of current post does not exist
            if len([i for i in parent.posts if i.relatedPost == value]) > 1:
                raise ValidationError("relatedPost must be unique.")

            related_posts = [i for i in parent.posts if i.id == value]

            # check that there are no multiple related posts,
            # that should never happen coz `id` is unique
            if len(related_posts) > 1:
                raise ValidationError("relatedPost can't be a link to more than one post.")

            # check that related post have another author
            if len(related_posts) == 1 and data["author"] == related_posts[0]["author"]:
                raise ValidationError("relatedPost can't have the same author.")

            # check that related post is not an answer to another post
            if len(related_posts) == 1 and related_posts[0]["relatedPost"]:
                raise ValidationError("relatedPost can't have relatedPost defined.")

            # check that answer author matches related post recipient
            if data["author"] and data["author"] != related_posts[0]["recipient"]:
                raise ValidationError("relatedPost invalid recipient.")

    def validate_recipient(self, data, value):
        # validate for aboveThresholdReviewers role
        if data["author"] in self.reviewer_roles and value not in self.recipient_roles:
            raise ValidationError("Value must be one of {}.".format(self.recipient_roles))

        # validate for complaint_owner and tender_owner roles
        elif data["author"] in self.recipient_roles and value not in self.reviewer_roles:
            raise ValidationError("Value must be one of {}.".format(self.reviewer_roles))


class Complaint(BaseComplaint):
    class Options:
        _base_roles = BaseComplaint.Options.roles
        roles = {
            "create": _base_roles["create"],  # TODO inherit the rest of the roles
            "draft": whitelist("author", "title", "description", "status"),
            "bot": whitelist("rejectReason", "status"),
            "cancellation": whitelist("cancellationReason", "status"),
            "satisfy": whitelist("satisfied", "status"),
            "escalate": whitelist("status"),
            "resolve": whitelist("status", "tendererAction"),
            "answer": whitelist("resolution", "resolutionType", "status", "tendererAction"),
            "action": whitelist("tendererAction"),
            "review": whitelist(
                "decision", "status",
                "rejectReason", "rejectReasonDescription",
                "reviewDate", "reviewPlace"
            ),
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
    rejectReasonDescription = StringType()
    reviewDate = IsoDateTimeType()
    reviewPlace = StringType()
    bid_id = StringType()
    posts = ListType(ModelType(ComplaintPost), default=list())

    def __acl__(self):
        return [
            (Allow, "g:bots", "edit_complaint"),
            (Allow, "g:aboveThresholdReviewers", "edit_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_complaint_documents"),
        ]

    def get_role(self):
        root = self.get_root()
        request = root.request
        data = request.json_body["data"]
        auth_role = request.authenticated_role
        status = data.get("status", self.status)
        if auth_role == "Administrator":
            role = auth_role
        elif auth_role == "complaint_owner" and self.status != "mistaken" and status == "cancelled":
            role = "cancellation"
        elif auth_role == "complaint_owner" and self.status in ["pending", "accepted"] and status == "stopping":
            role = "cancellation"
        elif auth_role == "complaint_owner" and self.status == "draft":
            role = "draft"
        elif auth_role == "complaint_owner" and self.status == "claim":
            role = "escalate"
        elif auth_role == "bots" and self.status == "draft":
            role = "bot"
        elif auth_role == "tender_owner" and self.status == "claim":
            role = "answer"
        elif auth_role == "tender_owner" and self.status in ["pending", "accepted"]:
            role = "action"
        elif auth_role == "tender_owner" and self.status == "satisfied":
            role = "resolve"
        elif auth_role == "complaint_owner" and self.status == "answered":
            role = "satisfy"
        elif auth_role == "aboveThresholdReviewers" and self.status in ["pending", "accepted", "stopping"]:
            role = "review"
        else:
            role = "invalid"
        return role

    def validate_cancellationReason(self, data, cancellationReason):
        if not cancellationReason and data.get("status") in ["cancelled", "stopping"]:
            raise ValidationError(u"This field is required.")

    def validate_rejectReason(self, data, rejectReason):
        tender_date = get_first_revision_date(get_tender(data["__parent__"]), default=get_now())
        if tender_date < RELEASE_2020_04_19:
            return
        if not rejectReason and data.get("status") in ["invalid", "stopped"] and data.get("type") == "complaint":
            raise ValidationError(u"This field is required.")

    def validate_reviewDate(self, data, reviewDate):
        tender_date = get_first_revision_date(get_tender(data["__parent__"]), default=get_now())
        if tender_date < RELEASE_2020_04_19:
            return
        if not reviewDate and data.get("status") == "accepted":
            raise ValidationError(u"This field is required.")

    def validate_reviewPlace(self, data, reviewPlace):
        tender_date = get_first_revision_date(get_tender(data["__parent__"]), default=get_now())
        if tender_date < RELEASE_2020_04_19:
            return
        if not reviewPlace and data.get("status") == "accepted":
            raise ValidationError(u"This field is required.")


class CancellationComplaint(Complaint):
    class Options:
        _base_roles = Complaint.Options.roles
        namespace = "Complaint"
        roles = {
            "create": whitelist("author", "title", "description", "relatedLot"),
            "draft": _base_roles["draft"],
            "bot": _base_roles["bot"],
            "cancellation": _base_roles["cancellation"],
            "satisfy": _base_roles["satisfy"],
            "resolve": _base_roles["resolve"],
            "action": _base_roles["action"],
            # "pending": whitelist("decision", "status", "rejectReason", "rejectReasonDescription"),
            "review": _base_roles["review"],
            "embedded": _base_roles["embedded"],
            "view": _base_roles["view"],
        }

    def get_role(self):
        root = self.get_root()
        request = root.request
        data = request.json_body["data"]
        auth_role = request.authenticated_role
        status = data.get("status", self.status)

        if auth_role == "Administrator":
            role = auth_role
        elif auth_role == "complaint_owner" and self.status != "mistaken" and status == "cancelled":
            role = "cancellation"
        elif auth_role == "complaint_owner" and self.status in ["pending", "accepted"] and status == "stopping":
            role = "cancellation"
        elif auth_role == "complaint_owner" and self.status == "draft":
            role = "draft"
        elif auth_role == "bots" and self.status == "draft":
            role = "bot"
        elif auth_role == "tender_owner" and self.status == "pending":
            role = "action"
        elif auth_role == "tender_owner" and self.status == "satisfied":
            role = "resolve"
        elif auth_role == "aboveThresholdReviewers" and self.status in ["pending", "accepted", "stopping"]:
            role = "review"
        else:
            role = "invalid"
        return role

    def __acl__(self):
        return [
            (Allow, "g:bots", "edit_complaint"),
            (Allow, "g:aboveThresholdReviewers", "edit_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_complaint_documents"),
        ]

    status = StringType(
        choices=[
            "draft",
            "pending",
            "accepted",
            "invalid",
            "resolved",
            "declined",
            "satisfied",
            "stopped",
            "mistaken",
        ],
        default="draft",
    )
    type = StringType(
        choices=["claim", "complaint"], default="complaint",
    )


class Cancellation(BaseCancellation):
    complaintPeriod = ModelType(Period)
    complaints = ListType(ModelType(CancellationComplaint), default=list())


class Award(BaseAward, QualificationMilestoneListMixin):
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
    """
    Data regarding tender process - publicly inviting
    prospective contractors to submit bids for evaluation and selecting a winner or winners.
    """

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

    procuring_entity_kinds = ["authority", "central", "defense", "general", "social", "special"]

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
                (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_contract"),
                (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_contract_documents"),
            ]
        )

        self._acl_cancellation_complaint(acl)
        return acl

    def validate_enquiryPeriod(self, data, period):
        # for deactivate validation to enquiryPeriod from parent class
        return

    def validate_tenderPeriod(self, data, period):
        if period:
            if is_new_created(data):
                validate_tender_period_start_date(data, period)
            validate_tender_period_duration(data, period, TENDERING_DURATION)

    @serializable(serialized_name="enquiryPeriod", type=ModelType(EnquiryPeriod))
    def tender_enquiryPeriod(self):
        end_date = calculate_tender_business_date(self.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME, self)
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
        end_date = calculate_complaint_business_date(self.tenderPeriod.endDate, -COMPLAINT_SUBMIT_TIME, self)
        return Period(dict(startDate=self.tenderPeriod.startDate, endDate=end_date))

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
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in self.awards
                if a.complaintPeriod and a.complaintPeriod.endDate
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
                    a.complaintPeriod.endDate.astimezone(TZ)
                    for a in lot_awards
                    if a.complaintPeriod and a.complaintPeriod.endDate
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

        extend_next_check_by_complaint_period_ends(self, checks)

        return min(checks).isoformat() if checks else None

    def check_auction_time(self):
        if check_auction_period(self.auctionPeriod, self):
            self.auctionPeriod.startDate = None
        for lot in self.lots:
            if check_auction_period(lot.auctionPeriod, self):
                lot.auctionPeriod.startDate = None

    def invalidate_bids_data(self):
        self.check_auction_time()
        self.enquiryPeriod.invalidationDate = get_now()
        for bid in self.bids:
            if bid.status not in ["deleted", "draft"]:
                bid.status = "invalid"
