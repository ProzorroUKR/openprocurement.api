from uuid import uuid4
from datetime import timedelta, datetime, time
from pyramid.security import Allow
from zope.interface import implementer
from schematics.types import StringType, MD5Type, BooleanType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.transforms import blacklist, whitelist, export_loop
from schematics.exceptions import ValidationError
from openprocurement.api.utils import get_now, get_first_revision_date, is_new_created
from openprocurement.api.constants import TZ
from openprocurement.api.auth import ACCR_3, ACCR_4, ACCR_5
from openprocurement.api.models import (
    Address,
    Period,
    Model,
    IsoDateTimeType,
    ListType,
    SifterListType,
    Identifier as BaseIdentifier,
    ContactPoint as BaseContactPoint,
)
from openprocurement.api.validation import validate_cpv_group, validate_items_uniq, validate_classification_id
from openprocurement.tender.core.models import (
    ITender,
    Bid as BaseBid,
    Contract as BaseContract,
    LotWithMinimalStepLimitsValidation as BaseLot,
    ConfidentialDocumentModelType,
    EUConfidentialDocument,
    EUDocument,
    LotValue as BaseLotValue,
    ComplaintModelType as BaseComplaintModelType,
    EnquiryPeriod,
    PeriodStartEndRequired,
    view_bid_role,
    Administrator_bid_role,
    schematics_default_role,
    schematics_embedded_role,
    embedded_lot_role,
    default_lot_role,
    get_tender,
    validate_lots_uniq,
    normalize_should_start_after,
    validate_parameters_uniq,
    bids_validation_wrapper,
    PROCURING_ENTITY_KINDS,
    QualificationMilestoneListMixin,
    RequirementResponse,
    BidResponsesMixin,

    # validators
    validate_response_requirement_uniq,
)
from openprocurement.tender.core.utils import (
    calculate_tender_business_date,
    calc_auction_end_time,
    has_unanswered_questions,
    has_unanswered_complaints,
    calculate_complaint_business_date,
    calculate_clarif_business_date,
    check_auction_period,
    calculate_tender_date,
    extend_next_check_by_complaint_period_ends,
)
from openprocurement.tender.belowthreshold.models import Tender as BaseTender
from openprocurement.tender.core.validation import (
    validate_lotvalue_value,
    validate_relatedlot,
)
from openprocurement.tender.openua.models import (
    Complaint as BaseComplaint,
    Award as BaseAward,
    Item as BaseItem,
    Tender as OpenUATender,
    Cancellation as BaseCancellation,
    Parameter,
)
from openprocurement.tender.openua.constants import COMPLAINT_SUBMIT_TIME, ENQUIRY_STAND_STILL_TIME
from openprocurement.tender.openeu.constants import (
    TENDERING_DURATION,
    QUESTIONS_STAND_STILL,
    TENDERING_AUCTION,
    BID_UNSUCCESSFUL_FROM,
)
from openprocurement.tender.openua.validation import (
    validate_tender_period_start_date,
    validate_tender_period_duration,
)


class IAboveThresholdEUTender(ITender):
    """ Marker interface for aboveThresholdEU tenders """


class BidModelType(ModelType):
    def export_loop(self, model_instance, field_converter, role=None, print_none=False):
        """
        Calls the main `export_loop` implementation because they are both
        supposed to operate on models.
        """
        if isinstance(model_instance, self.model_class):
            model_class = model_instance.__class__
        else:
            model_class = self.model_class

        tender = model_instance.__parent__
        tender_date = get_first_revision_date(tender, default=get_now())
        status = getattr(model_instance, "status")
        if tender_date > BID_UNSUCCESSFUL_FROM and role not in [None, "plain"] and status == "unsuccessful":
            role = "bid.unsuccessful"

        shaped = export_loop(model_class, model_instance, field_converter, role=role, print_none=print_none)

        if shaped and len(shaped) == 0 and self.allow_none():
            return shaped
        elif shaped:
            return shaped
        elif print_none:
            return shaped


class ComplaintModelType(BaseComplaintModelType):
    view_claim_statuses = [
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
        "active.auction",
    ]


class Item(BaseItem):
    """A good, service, or work to be contracted."""

    description_en = StringType(required=True, min_length=1)


class Identifier(BaseIdentifier):

    legalName_en = StringType(required=True, min_length=1)


class ContactPoint(BaseContactPoint):

    name_en = StringType(required=True, min_length=1)
    availableLanguage = StringType(required=True, choices=["uk", "en", "ru"], default="uk")


class Organization(Model):
    """An organization."""

    class Options:
        roles = {"embedded": schematics_embedded_role, "view": schematics_default_role}

    name = StringType(required=True)
    name_en = StringType(required=True, min_length=1)
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier, required=True))
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True), required=False)


class ProcuringEntity(Organization):
    """An organization."""

    class Options:
        roles = {
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
            "edit_active.tendering": schematics_default_role + blacklist("kind"),
        }

    kind = StringType(choices=PROCURING_ENTITY_KINDS)


class Contract(BaseContract):
    documents = ListType(ModelType(EUDocument, required=True), default=list())
    items = ListType(ModelType(Item, required=True))


class Complaint(BaseComplaint):
    documents = ListType(ModelType(EUDocument, required=True), default=list())

    def serialize(self, role=None, context=None):
        if (
            role == "view"
            and self.type == "claim"
            and get_tender(self).status
            in [
                "active.tendering",
                "active.pre-qualification",
                "active.pre-qualification.stand-still",
                "active.auction",
            ]
        ):
            role = "view_claim"
        return super(Complaint, self).serialize(role=role, context=context)


class Cancellation(BaseCancellation):
    class Options:
        roles = {
            "create": whitelist("reason", "status", "reasonType", "cancellationOf", "relatedLot"),
            "edit": whitelist("status", "reasonType"),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }

    documents = ListType(ModelType(EUDocument, required=True), default=list())


class TenderAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        tender = self.__parent__
        if tender.lots or tender.status not in [
            "active.tendering",
            "active.pre-qualification.stand-still",
            "active.auction",
        ]:
            return
        start_after = None
        if tender.status == "active.tendering" and tender.tenderPeriod.endDate:
            start_after = calculate_tender_date(tender.tenderPeriod.endDate, TENDERING_AUCTION, tender)
        elif self.startDate and get_now() > calc_auction_end_time(tender.numberOfBids, self.startDate):
            start_after = calc_auction_end_time(tender.numberOfBids, self.startDate)
        elif tender.qualificationPeriod and tender.qualificationPeriod.endDate:
            decision_dates = [
                datetime.combine(
                    complaint.dateDecision.date() + timedelta(days=3), time(0, tzinfo=complaint.dateDecision.tzinfo)
                )
                for qualification in tender.qualifications
                for complaint in qualification.complaints
                if complaint.dateDecision
            ]
            decision_dates.append(tender.qualificationPeriod.endDate)
            start_after = max(decision_dates)
        if start_after:
            return normalize_should_start_after(start_after, tender).isoformat()


class LotAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        tender = get_tender(self)
        lot = self.__parent__
        statuses = ["active.tendering", "active.pre-qualification.stand-still", "active.auction"]
        if tender.status not in statuses or lot.status != "active":
            return
        start_after = None
        if tender.status == "active.tendering" and tender.tenderPeriod.endDate:
            start_after = calculate_tender_date(tender.tenderPeriod.endDate, TENDERING_AUCTION, tender)
        elif self.startDate and get_now() > calc_auction_end_time(lot.numberOfBids, self.startDate):
            start_after = calc_auction_end_time(lot.numberOfBids, self.startDate)
        elif tender.qualificationPeriod and tender.qualificationPeriod.endDate:
            decision_dates = [
                datetime.combine(
                    complaint.dateDecision.date() + timedelta(days=3), time(0, tzinfo=complaint.dateDecision.tzinfo)
                )
                for qualification in tender.qualifications
                for complaint in qualification.complaints
                if complaint.dateDecision
            ]
            decision_dates.append(tender.qualificationPeriod.endDate)
            start_after = max(decision_dates)
        if start_after:
            return normalize_should_start_after(start_after, tender).isoformat()


class Lot(BaseLot):
    class Options:
        roles = {
            "create": whitelist(
                "id",
                "title",
                "title_en",
                "title_ru",
                "description",
                "description_en",
                "description_ru",
                "value",
                "guarantee",
                "minimalStep",
            ),
            "edit": whitelist(
                "title",
                "title_en",
                "title_ru",
                "description",
                "description_en",
                "description_ru",
                "value",
                "guarantee",
                "minimalStep",
            ),
            "embedded": embedded_lot_role,
            "view": default_lot_role,
            "default": default_lot_role,
            "auction_view": default_lot_role,
            "auction_patch": whitelist("id", "auctionUrl"),
            "chronograph": whitelist("id", "auctionPeriod"),
            "chronograph_view": whitelist("id", "auctionPeriod", "numberOfBids", "status"),
        }

    auctionPeriod = ModelType(LotAuctionPeriod, default={})

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        bids = [
            bid
            for bid in self.__parent__.bids
            if self.id in [i.relatedLot for i in bid.lotValues if i.status in ["active", "pending"]]
            and bid.status in ["active", "pending"]
        ]
        return len(bids)


class LotValue(BaseLotValue):
    class Options:
        roles = {
            "create": whitelist("value", "relatedLot", "subcontractingDetails"),
            "edit": whitelist("value", "relatedLot", "subcontractingDetails"),
            "auction_view": whitelist("value", "date", "relatedLot", "participationUrl", "status"),
        }

    subcontractingDetails = StringType()
    status = StringType(choices=["pending", "active", "unsuccessful"], default="pending")

    skip = ("invalid", "deleted", "draft")

    def validate_value(self, data, value):
        parent = data["__parent__"]
        if isinstance(parent, Model) and parent.status not in self.skip:
            validate_lotvalue_value(get_tender(parent), data["relatedLot"], value)

    def validate_relatedLot(self, data, relatedLot):
        parent = data["__parent__"]
        if isinstance(parent, Model) and parent.status not in self.skip:
            validate_relatedlot(get_tender(parent), relatedLot)


class Bid(BidResponsesMixin, BaseBid):
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
                "financialDocuments",
                "eligibilityDocuments",
                "qualificationDocuments",
                "requirementResponses",
            ),
            "edit": whitelist(
                "value",
                "tenderers",
                "parameters",
                "lotValues",
                "status",
                "subcontractingDetails",
                "requirementResponses",
            ),
            "auction_view": whitelist("value", "lotValues", "id", "date", "parameters", "participationUrl", "status"),
            "auction_post": whitelist("value", "lotValues", "id", "date"),
            "auction_patch": whitelist("id", "lotValues", "participationUrl"),
            "active.enquiries": whitelist(),
            "active.tendering": whitelist(),
            "active.pre-qualification": whitelist(
                "id", "status", "documents", "eligibilityDocuments", "tenderers", "requirementResponses"),
            "active.pre-qualification.stand-still": whitelist(
                "id", "status", "documents", "eligibilityDocuments", "tenderers", "requirementResponses"),
            "active.auction": whitelist("id", "status", "documents", "eligibilityDocuments", "tenderers"),
            "active.qualification": view_bid_role,
            "active.awarded": view_bid_role,
            "complete": view_bid_role,
            "unsuccessful": view_bid_role,
            "bid.unsuccessful": whitelist(
                "id",
                "status",
                "tenderers",
                "documents",
                "eligibilityDocuments",
                "parameters",
                "selfQualified",
                "selfEligible",
                "subcontractingDetails",
                "requirementResponses",
            ),
            "cancelled": view_bid_role,
            "invalid": whitelist("id", "status"),
            "invalid.pre-qualification": whitelist(
                "id", "status", "documents", "eligibilityDocuments", "tenderers", "requirementResponses"),
            "deleted": whitelist("id", "status"),
        }

    documents = ListType(ConfidentialDocumentModelType(EUConfidentialDocument, required=True), default=list())
    financialDocuments = ListType(ConfidentialDocumentModelType(EUConfidentialDocument, required=True), default=list())
    eligibilityDocuments = ListType(ConfidentialDocumentModelType(EUConfidentialDocument, required=True), default=list())
    qualificationDocuments = ListType(ConfidentialDocumentModelType(EUConfidentialDocument, required=True), default=list())
    lotValues = ListType(ModelType(LotValue, required=True), default=list())
    selfQualified = BooleanType(required=True, choices=[True])
    selfEligible = BooleanType(choices=[True])
    subcontractingDetails = StringType()
    parameters = ListType(ModelType(Parameter, required=True), default=list(), validators=[validate_parameters_uniq])
    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
        default="pending",
    )

    def serialize(self, role=None):
        if role and role != "create" and self.status in ["invalid", "invalid.pre-qualification", "deleted"]:
            role = self.status
        elif role and role != "create" and self.status == "unsuccessful":
            role = "bid.unsuccessful"
        return super(Bid, self).serialize(role)

    @serializable(serialized_name="status")
    def serialize_status(self):
        if self.status in [
            "draft",
            "invalid",
            "invalid.pre-qualification",
            "unsuccessful",
            "deleted",
        ] or self.__parent__.status in ["active.tendering", "cancelled"]:
            return self.status
        if self.__parent__.lots:
            active_lots = [lot.id for lot in self.__parent__.lots if lot.status in ("active", "complete")]
            if not self.lotValues:
                return "invalid"
            elif [i.relatedLot for i in self.lotValues if i.status == "pending" and i.relatedLot in active_lots]:
                return "pending"
            elif [i.relatedLot for i in self.lotValues if i.status == "active" and i.relatedLot in active_lots]:
                return "active"
            else:
                return "unsuccessful"
        return self.status

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


class Award(BaseAward):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """

    complaints = ListType(ModelType(Complaint, required=True), default=list())
    items = ListType(ModelType(Item, required=True))
    documents = ListType(ModelType(EUDocument, required=True), default=list())
    qualified = BooleanType()
    eligible = BooleanType()

    def validate_qualified(self, data, qualified):
        pass

    def validate_eligible(self, data, eligible):
        pass


class Qualification(QualificationMilestoneListMixin):
    """ Pre-Qualification """

    class Options:
        roles = {
            "create": blacklist("id", "status", "documents", "date", "requirementResponses"),
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
                "requirementResponses",
            ),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }

    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    bidID = StringType(required=True)
    lotID = MD5Type()
    status = StringType(choices=["pending", "active", "unsuccessful", "cancelled"], default="pending")
    date = IsoDateTimeType()
    documents = ListType(ModelType(EUDocument, required=True), default=list())
    complaints = ListType(ModelType(Complaint, required=True), default=list())
    qualified = BooleanType(default=False)
    eligible = BooleanType(default=False)

    requirementResponses = ListType(
        ModelType(RequirementResponse, required=True),
        default=list()
    )

    def validate_qualified(self, data, qualified):
        if data["status"] == "active" and not qualified:
            raise ValidationError(u"This field is required.")

    def validate_eligible(self, data, eligible):
        if data["status"] == "active" and not eligible:
            raise ValidationError(u"This field is required.")

    def validate_lotID(self, data, lotID):
        parent = data["__parent__"]
        if isinstance(parent, Model):
            if not lotID and parent.lots:
                raise ValidationError(u"This field is required.")
            if lotID and lotID not in [lot.id for lot in parent.lots if lot]:
                raise ValidationError(u"lotID should be one of lots")


@implementer(IAboveThresholdEUTender)
class Tender(BaseTender):
    """ OpenEU tender model """

    class Options:
        namespace = "Tender"
        _parent_roles = BaseTender.Options.roles

        _edit_role = _parent_roles["edit"] - whitelist("enquiryPeriod")
        _read_fields = whitelist("qualifications", "qualificationPeriod", "complaintPeriod")
        _tendering_role = _parent_roles["active.tendering"] + _read_fields + whitelist("tender_enquiryPeriod")
        _view_role = _parent_roles["view"] + _read_fields
        _pre_qualifications_role = _view_role

        _all_forbidden = whitelist()
        roles = {
            "create": _parent_roles["create"] - whitelist("enquiryPeriod"),
            "edit": _edit_role,
            "edit_draft": _edit_role,
            "edit_active.tendering": _edit_role,
            "edit_active.pre-qualification": whitelist("status"),
            "edit_active.pre-qualification.stand-still": _all_forbidden,
            "edit_active.auction": _all_forbidden,
            "edit_active.qualification": _all_forbidden,
            "edit_active.awarded": _all_forbidden,
            "edit_complete": _all_forbidden,
            "edit_unsuccessful": _all_forbidden,
            "edit_cancelled": _all_forbidden,
            "active.pre-qualification": _pre_qualifications_role,
            "active.pre-qualification.stand-still": _pre_qualifications_role,
            "active.auction": _pre_qualifications_role,
            "draft": _tendering_role,
            "active.tendering": _tendering_role,
            "active.qualification": _view_role,
            "active.awarded": _view_role,
            "complete": _view_role,
            "unsuccessful": _view_role,
            "cancelled": _view_role,
            "view": _view_role,
            "auction_view": _parent_roles["auction_view"],
            "auction_post": _parent_roles["auction_post"],
            "auction_patch": _parent_roles["auction_patch"],
            "chronograph": _parent_roles["chronograph"],
            "chronograph_view": _parent_roles["chronograph_view"],
            "Administrator": _parent_roles["Administrator"],
            "default": _parent_roles["default"],
            "plain": _parent_roles["plain"],
            "contracting": _parent_roles["contracting"],
            "listing": _parent_roles["listing"],
        }

    procurementMethodType = StringType(default="aboveThresholdEU")
    title_en = StringType(required=True, min_length=1)

    enquiryPeriod = ModelType(EnquiryPeriod, required=False)
    tenderPeriod = ModelType(PeriodStartEndRequired, required=True)
    auctionPeriod = ModelType(TenderAuctionPeriod, default={})
    documents = ListType(
        ModelType(EUDocument, required=True), default=list()
    )  # All documents and attachments related to the tender.
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
    )  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    complaints = ListType(ComplaintModelType(Complaint, required=True), default=list())
    contracts = ListType(ModelType(Contract, required=True), default=list())
    cancellations = ListType(ModelType(Cancellation, required=True), default=list())
    awards = ListType(ModelType(Award, required=True), default=list())
    procuringEntity = ModelType(
        ProcuringEntity, required=True
    )  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    bids = SifterListType(
        BidModelType(Bid),
        default=list(),
        filter_by="status",
        filter_in_values=["invalid", "invalid.pre-qualification", "deleted"],
    )  # A list of all the companies who entered submissions for the tender.
    qualifications = ListType(ModelType(Qualification, required=True), default=list())
    qualificationPeriod = ModelType(Period)
    lots = ListType(ModelType(Lot, required=True), default=list(), validators=[validate_lots_uniq])
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.auction",
            "active.qualification",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
        ],
        default="active.tendering",
    )

    create_accreditations = (ACCR_3, ACCR_5)
    central_accreditations = (ACCR_5,)
    edit_accreditations = (ACCR_4,)

    procuring_entity_kinds = ["authority", "central", "defense", "general", "social", "special"]

    block_tender_complaint_status = OpenUATender.block_tender_complaint_status
    block_complaint_status = OpenUATender.block_complaint_status

    def __acl__(self):
        acl = [
            (Allow, "{}_{}".format(i.owner, i.owner_token), "create_qualification_complaint")
            for i in self.bids
            if i.status in ["active", "unsuccessful"]
        ]
        acl.extend(
            [
                (Allow, "{}_{}".format(i.owner, i.owner_token), "create_award_complaint")
                for i in self.bids
                if i.status == "active"
            ]
        )
        acl.extend(
            [
                (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_complaint"),
                (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_contract"),
                (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_contract_documents"),
                (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_qualification_documents"),
            ]
        )

        self._acl_cancellation_complaint(acl)
        return acl

    def validate_enquiryPeriod(self, data, period):
        # for deactivate validation to enquiryPeriod from parent class
        return

    @serializable(serialized_name="enquiryPeriod", type=ModelType(EnquiryPeriod))
    def tender_enquiryPeriod(self):
        end_date = calculate_tender_business_date(self.tenderPeriod.endDate, -QUESTIONS_STAND_STILL, self)
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
            self.status == "active.pre-qualification.stand-still"
            and self.qualificationPeriod
            and self.qualificationPeriod.endDate
        ):
            active_lots = [lot.id for lot in self.lots if lot.status == "active"] if self.lots else [None]
            if not any(
                [
                    i.status in self.block_complaint_status
                    for q in self.qualifications
                    for i in q.complaints
                    if q.lotID in active_lots
                ]
            ):
                checks.append(self.qualificationPeriod.endDate.astimezone(TZ))
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
        if self.status and self.status.startswith("active"):
            for award in self.awards:
                if award.status == "active" and not any([i.awardID == award.id for i in self.contracts]):
                    checks.append(award.date)

        extend_next_check_by_complaint_period_ends(self, checks)

        return min(checks).isoformat() if checks else None

    def validate_tenderPeriod(self, data, period):
        if is_new_created(data):
            validate_tender_period_start_date(data, period)
        validate_tender_period_duration(data, period, TENDERING_DURATION)

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        return len([bid for bid in self.bids if bid.status in ("active", "pending")])

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
