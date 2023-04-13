from pyramid.security import Allow
from schematics.transforms import whitelist
from schematics.types import IntType, URLType, BooleanType
from schematics.types import StringType
from schematics.types.compound import ModelType
from zope.interface import implementer
from schematics.types.serializable import serializable
from openprocurement.api.constants import TZ, CPV_ITEMS_CLASS_FROM
from schematics.exceptions import ValidationError
from decimal import Decimal
from openprocurement.api.auth import ACCR_3, ACCR_4, ACCR_5
from openprocurement.api.models import Period, ListType, SifterListType, IsoDurationType
from openprocurement.api.utils import get_now, is_new_created, get_first_revision_date
from openprocurement.api.validation import validate_cpv_group, validate_items_uniq, validate_classification_id
from openprocurement.tender.cfaua.validation import validate_max_awards_number, validate_max_agreement_duration_period
from openprocurement.tender.cfaua.interfaces import ICloseFrameworkAgreementUA
from openprocurement.tender.cfaua.models.submodels.agreement import Agreement
from openprocurement.tender.cfaua.models.submodels.award import Award
from openprocurement.tender.cfaua.models.submodels.bids import BidModelType, Bid
from openprocurement.tender.cfaua.models.submodels.cancellation import Cancellation
from openprocurement.tender.cfaua.models.submodels.complaint import (
    ComplaintPolyModelType,
    Complaint,
    Claim,
)
from openprocurement.tender.openua.models import get_complaint_type_model
from openprocurement.tender.cfaua.models.submodels.item import Item
from openprocurement.tender.cfaua.models.submodels.guarantee import Guarantee
from openprocurement.tender.cfaua.models.submodels.feature import Feature
from openprocurement.tender.cfaua.models.submodels.lot import Lot
from openprocurement.tender.cfaua.models.submodels.organization import ProcuringEntity
from openprocurement.tender.cfaua.models.submodels.periods import TenderAuctionPeriod, ContractPeriod
from openprocurement.tender.cfaua.models.submodels.qualification import Qualification
from openprocurement.tender.cfaua.models.submodels.value import Value
from openprocurement.tender.cfaua.constants import QUESTIONS_STAND_STILL
from openprocurement.tender.openua.constants import ENQUIRY_STAND_STILL_TIME
from openprocurement.tender.core.models import (
    EnquiryPeriod, PeriodStartEndRequired, validate_lots_uniq,
    validate_features_uniq, default_status, Question, Tender, EUDocument,
    validate_item_related_buyers,
)
from openprocurement.tender.core.validation import validate_minimalstep, validate_tender_period_duration
from openprocurement.tender.openua.constants import COMPLAINT_SUBMIT_TIME
from openprocurement.tender.core.utils import (
    check_auction_period,
    calculate_complaint_business_date,
    calculate_tender_business_date,
    calculate_clarif_business_date,
    calc_auction_end_time,
    has_unanswered_questions,
    has_unanswered_complaints,
    extend_next_check_by_complaint_period_ends,
    cancellation_block_tender,
    validate_features_custom_weight,
)
from openprocurement.tender.cfaua.constants import TENDERING_DURATION
from openprocurement.tender.openua.validation import (
    _validate_tender_period_start_date,
)


@implementer(ICloseFrameworkAgreementUA)
class CloseFrameworkAgreementUA(Tender):
    """ OpenEU tender model """

    class Options:
        namespace = "Tender"
        _core_roles = Tender.Options.roles
        _procurement_method_details = whitelist("procurementMethodDetails")
        _edit_fields = _core_roles["edit"] + whitelist(
            "tenderPeriod",
            "features",
            "complaintPeriod",
            "agreementDuration",
            "next_check",
            "procuringEntity",
            "guarantee",
            "tender_enquiryPeriod",
            "minimalStep",
            "items",
            "qualificationPeriod",
            "value",
            "maxAwardsCount",
            "agreements",
            "numberOfBidders",
            "hasEnquiries",
            "tender_guarantee",
            "tender_value",
            "tender_minimalStep",
        )
        _edit_role = _edit_fields + whitelist("numberOfBids")
        _edit_qualification = whitelist("status") + _procurement_method_details
        _tendering_view_role = (
            _core_roles["view"]
            + _edit_fields
            + whitelist(
                "auctionPeriod",
                "lots",
                "enquiryPeriod",
                "complaints",
                "auctionUrl",
                "awardPeriod",
                "qualifications",
                "questions",
                "cancellations",
                "awards",
            )
        )
        _view_role = _tendering_view_role + whitelist("numberOfBids", "bids")
        _complete_view_role = _view_role + whitelist("contractPeriod")
        roles = {
            "create": _edit_role + whitelist("mode", "procurementMethodType", "lots"),
            "edit_draft": _edit_role + whitelist("status"),
            "edit": _edit_role,
            "edit_active.tendering": _edit_role,
            "edit_active.pre-qualification": _edit_qualification,
            "edit_active.qualification": _edit_qualification,
            "edit_cancelled": _procurement_method_details,
            "edit_complete": _procurement_method_details,
            "edit_unsuccessful": _procurement_method_details,
            "edit_active.awarded": _procurement_method_details,
            "edit_active.auction": _procurement_method_details,
            "edit_active.pre-qualification.stand-still": _procurement_method_details,
            "draft": _tendering_view_role + whitelist("contractPeriod"),
            "active.tendering": _tendering_view_role,
            "cancelled": _view_role,
            "active.auction": _view_role,
            "active.pre-qualification.stand-still": _view_role,
            "active.qualification.stand-still": _view_role,
            "view": _complete_view_role,
            "active.qualification": _complete_view_role,
            "active.pre-qualification": _complete_view_role,
            "complete": _complete_view_role,
            "active.awarded": _complete_view_role,
            "unsuccessful": _complete_view_role,
            "contracting": _core_roles["contracting"] + _procurement_method_details,
            "chronograph": _core_roles["chronograph"] + _procurement_method_details,
            "chronograph_view": _core_roles["chronograph_view"] + _procurement_method_details,
            "auction_view": _core_roles["auction_view"]
            + _procurement_method_details
            + whitelist("milestones", "mainProcurementCategory"),
            "Administrator": _core_roles["Administrator"] + _procurement_method_details,
            "auction_post": _core_roles["auction_post"] + _procurement_method_details,
            "auction_patch": _core_roles["auction_patch"] + _procurement_method_details,
            "listing": _core_roles["listing"] + _procurement_method_details,
            "embedded": _core_roles["embedded"],
            "plain": _core_roles["plain"],
            "default": _core_roles["default"],
        }

    create_accreditations = (ACCR_3, ACCR_5)
    central_accreditations = (ACCR_5,)
    edit_accreditations = (ACCR_4,)

    procuring_entity_kinds = ["authority", "central", "defense", "general", "social", "special"]
    block_tender_complaint_status = ["claim", "pending", "accepted", "satisfied", "stopping"]
    block_complaint_status = ["pending", "accepted", "satisfied", "stopping"]

    auctionPeriod = ModelType(TenderAuctionPeriod, default={})
    auctionUrl = URLType()
    awards = ListType(ModelType(Award, required=True), default=list())
    awardPeriod = ModelType(Period)  # The dat e or period on which an award is anticipated to be made.
    bids = SifterListType(
        BidModelType(Bid),
        default=list(),
        filter_by="status",
        filter_in_values=["invalid", "invalid.pre-qualification", "deleted"],
    )  # A list of all the companies who entered submissions for the tender.
    cancellations = ListType(ModelType(Cancellation, required=True), default=list())
    complaints = ListType(
        ComplaintPolyModelType(
            [Complaint, Claim],
            claim_function=get_complaint_type_model,
            required=True,
        ),
        default=list(),
    )
    contractPeriod = ModelType(ContractPeriod, required=False)
    agreements = ListType(ModelType(Agreement, required=True), default=list())
    documents = ListType(
        ModelType(EUDocument, required=True), default=list()
    )  # All documents and attachments related to the tender.
    enquiryPeriod = ModelType(EnquiryPeriod, required=False)
    guarantee = ModelType(Guarantee)
    hasEnquiries = BooleanType()  # A Yes/No field as to whether enquiries were part of tender process.
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
    )  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    minimalStep = ModelType(Value)
    numberOfBidders = IntType()  # The number of unique tenderers who participated in the tender
    maxAwardsCount = IntType(required=True, validators=[validate_max_awards_number])
    lots = ListType(
        ModelType(Lot, required=True), min_size=1, max_size=1, default=list(), validators=[validate_lots_uniq]
    )
    procurementMethodType = StringType(default="closeFrameworkAgreementUA")
    procuringEntity = ModelType(
        ProcuringEntity, required=True
    )  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    qualificationPeriod = ModelType(Period)
    qualifications = ListType(ModelType(Qualification, required=True), default=list())
    questions = ListType(ModelType(Question, required=True), default=list())
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.auction",
            "active.qualification",
            "active.qualification.stand-still",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
        ],
        default=default_status(),
    )
    tenderPeriod = ModelType(PeriodStartEndRequired, required=True)
    title_en = StringType(required=True, min_length=1)
    value = ModelType(Value, required=True)  # The total estimated value of the procurement.
    agreementDuration = IsoDurationType(required=True, validators=[validate_max_agreement_duration_period])
    mainProcurementCategory = StringType(choices=["goods", "services"])

    def __local_roles__(self):
        roles = dict([("{}_{}".format(self.owner, self.owner_token), "tender_owner")])
        for i in self.bids:
            roles["{}_{}".format(i.owner, i.owner_token)] = "bid_owner"
        return roles

    def __acl__(self):
        acl = [
            (Allow, "{}_{}".format(i.owner, i.owner_token), "create_qualification_complaint")
            for i in self.bids
            if i.status in ["active", "unsuccessful", "invalid.pre-qualification"]
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
                (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_qualification_documents"),
            ]
        )
        self._acl_cancellation_complaint(acl)
        return acl

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

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        complaint_period_class = self._fields["tenderPeriod"]
        end_date = calculate_complaint_business_date(self.tenderPeriod.endDate, -COMPLAINT_SUBMIT_TIME, self)
        return complaint_period_class(dict(startDate=self.tenderPeriod.startDate, endDate=end_date))

    @serializable(
        serialized_name="enquiryPeriod", serialize_when_none=True, type=ModelType(EnquiryPeriod, required=False)
    )
    def tender_enquiryPeriod(self):
        enquiry_period_class = self._fields["enquiryPeriod"]
        end_date = calculate_tender_business_date(self.tenderPeriod.endDate, -QUESTIONS_STAND_STILL, self)
        clarifications_until = calculate_clarif_business_date(end_date, ENQUIRY_STAND_STILL_TIME, self, True)
        return enquiry_period_class(
            dict(
                startDate=self.tenderPeriod.startDate,
                endDate=end_date,
                invalidationDate=self.enquiryPeriod and self.enquiryPeriod.invalidationDate,
                clarificationsUntil=clarifications_until,
            )
        )

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def tender_guarantee(self):
        return self.guarantee
        # if self.lots:
        #     lots_amount = [i.guarantee.amount for i in self.lots if i.guarantee]
        #     if not lots_amount:
        #         return self.guarantee
        #     guarantee = {"amount": sum(lots_amount)}
        #     lots_currency = [i.guarantee.currency for i in self.lots if i.guarantee]
        #     guarantee["currency"] = lots_currency[0] if lots_currency else None
        #     if self.guarantee:
        #         guarantee["currency"] = self.guarantee.currency
        #     guarantee_class = self._fields["guarantee"]
        #     return guarantee_class(guarantee)
        # else:
        #     return self.guarantee

    @serializable(serialized_name="minimalStep", serialize_when_none=False, type=ModelType(Value, required=True))
    def tender_minimalStep(self):
        return self.minimalStep
        # if self.lots:
        #     minimalStep = self._fields["minimalStep"]
        #     return minimalStep(
        #         dict(
        #             amount=min([i.minimalStep.amount for i in self.lots]),
        #             currency=self.minimalStep.currency,
        #             valueAddedTaxIncluded=self.minimalStep.valueAddedTaxIncluded,
        #         )
        #     )
        # else:
        #     return self.minimalStep

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
        elif self.status == "active.qualification.stand-still" and self.awardPeriod and self.awardPeriod.endDate:
            active_lots = [lot.id for lot in self.lots if lot.status == "active"] if self.lots else [None]
            if not any(
                [
                    i.status in self.block_complaint_status
                    for q in self.qualifications
                    for i in q.complaints
                    if q.lotID in active_lots
                ]
            ):
                checks.append(self.awardPeriod.endDate.astimezone(TZ))

        return min(checks).isoformat() if checks else None

    @serializable
    def numberOfBids(self):
        return len([bid for bid in self.bids if bid.status in ("active", "pending")])

    @serializable(serialized_name="value", type=ModelType(Value))
    def tender_value(self):
        return self.value
    #     value_class = self._fields["value"]
    #     return (
    #         value_class(
    #             dict(
    #                 amount=sum([i.value.amount for i in self.lots]),
    #                 currency=self.value.currency,
    #                 valueAddedTaxIncluded=self.value.valueAddedTaxIncluded,
    #             )
    #         )
    #         if self.lots
    #         else self.value
    # )

    def validate_auctionUrl(self, data, url):
        if url and data["lots"]:
            raise ValidationError("url should be posted for each lot")

    def validate_awardPeriod(self, data, period):
        if (
            period
            and period.startDate
            and data.get("auctionPeriod")
            and data.get("auctionPeriod").endDate
            and period.startDate < data.get("auctionPeriod").endDate
        ):
            raise ValidationError("period should begin after auctionPeriod")
        if (
            period
            and period.startDate
            and data.get("tenderPeriod")
            and data.get("tenderPeriod").endDate
            and period.startDate < data.get("tenderPeriod").endDate
        ):
            raise ValidationError("period should begin after tenderPeriod")

    def validate_features(self, data, features):
        if features:
            for i in features:
                if i.featureOf == "lot":
                    raise ValidationError("Features are not allowed for lots")
        validate_features_custom_weight(data, features, Decimal("0.3"))

    def validate_items(self, data, items):
        cpv_336_group = items[0].classification.id[:3] == "336" if items else False
        date = get_first_revision_date(data, default=get_now())
        if (
                not cpv_336_group and date > CPV_ITEMS_CLASS_FROM and items
                and len(set([i.classification.id[:4] for i in items])) != 1
        ):
            raise ValidationError("CPV class of items should be identical")
        else:
            validate_cpv_group(items)
        validate_item_related_buyers(data, items)

    def validate_lots(self, data, lots):
        if len(set([lot.guarantee.currency for lot in lots if lot.guarantee])) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")

    def validate_minimalStep(self, data, value):
        validate_minimalstep(data, value)

    def validate_tenderPeriod(self, data, period):
        if period:
            if is_new_created(data):
                _validate_tender_period_start_date(data, period)
            validate_tender_period_duration(data, period, TENDERING_DURATION)
