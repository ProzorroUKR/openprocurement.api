# -*- coding: utf-8 -*-
from openprocurement.tender.cfaselectionua.interfaces import ICFASelectionUATender
from openprocurement.tender.cfaselectionua.models.submodels.agreement import Agreement
from openprocurement.tender.cfaselectionua.models.submodels.award import Award
from openprocurement.tender.cfaselectionua.models.submodels.bid import Bid
from openprocurement.tender.cfaselectionua.models.submodels.contract import Contract
from openprocurement.tender.cfaselectionua.models.submodels.feature import Feature
from openprocurement.tender.cfaselectionua.models.submodels.item import Item
from openprocurement.tender.cfaselectionua.models.submodels.lot import Lot
from openprocurement.tender.cfaselectionua.models.submodels.organizationAndPocuringEntity import ProcuringEntity
from schematics.types import StringType, IntType, URLType, BooleanType
from schematics.types.compound import ModelType
from schematics.transforms import whitelist
from zope.interface import implementer, provider
from pyramid.security import Allow
from openprocurement.api.models import ListType, Period, Value, Guarantee
from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.models import (
    validate_lots_uniq,
    TenderAuctionPeriod,
    PeriodEndRequired,
    Tender as BaseTender,
    Cancellation as BaseCancellation,
    validate_features_uniq,
)


class Cancellation(BaseCancellation):
    _before_release_reasonType_choices = []

    _after_release_status_choices = ["draft", "unsuccessful", "active"]


@implementer(ICFASelectionUATender)
@provider(ICFASelectionUATender)
class CFASelectionUATender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors
    to submit bids for evaluation and selecting a winner or winners.
    """

    class Options:
        namespace = "Tender"
        _core_roles = BaseTender.Options.roles
        _not_implemented = whitelist("mainProcurementCategory", "milestones")
        _base_edit = (
            _core_roles["edit"]
            - _not_implemented
            + whitelist(
                "procuringEntity",
                "numberOfBidders",
                "serializable_guarantee",
                "items",
                "next_check",
                "tender_guarantee",
                "numberOfBids",
                "agreements",
                "hasEnquiries",
            )
        )
        _edit_role = _base_edit + whitelist(
            "enquiryPeriod", "tender_minimalStep", "contracts", "tenderPeriod", "features", "serializable_minimalStep"
        )
        _draft_view_role = (
            _core_roles["view"]
            - _not_implemented
            + whitelist(
                "tender_guarantee",
                "awardPeriod",
                "auctionUrl",
                "auctionPeriod",
                "next_check",
                "procuringEntity",
                "questions",
                "complaints",
                "lots",
                "items",
                "cancellations",
                "contracts",
                "agreements",
                "numberOfBidders",
                "awards",
                "serializable_guarantee",
                "hasEnquiries",
            )
        )
        _view_tendering_role = _draft_view_role + whitelist(
            "tender_value",
            "tenderPeriod",
            "features",
            "enquiryPeriod",
            "tender_minimalStep",
            "serializable_value",
            "serializable_minimalStep",
        )
        _view_role = _view_tendering_role + whitelist("bids", "numberOfBids")
        _procurement_method_details = whitelist("procurementMethodDetails")
        roles = {
            "create": _base_edit + whitelist("lots", "procurementMethodType", "mode"),
            "edit_draft": _core_roles["edit_draft"] + _procurement_method_details,
            "edit_draft.pending": whitelist("agreements", "unsuccessfulReason") + _procurement_method_details,
            "edit_cancelled": _procurement_method_details,
            "edit_complete": _procurement_method_details,
            "edit_unsuccessful": _procurement_method_details,
            "edit_active.awarded": _procurement_method_details,
            "edit_active.auction": _procurement_method_details,
            "edit_active.tendering": _procurement_method_details,
            "edit_active.qualification": _procurement_method_details,
            "edit_active.enquiries": whitelist(
                "description",
                "description_en",
                "description_ru",
                "documents",
                "items",
                "lots",
                "procurementMethodDetails",
                "serializable_guarantee",
                "tenderPeriod",
                "tender_guarantee",
                "title",
                "title_en",
                "title_ru",
            ),
            "edit": _edit_role,
            "edit_agreement_selection": whitelist("agreements", "procurementMethodDetails", "status"),
            "active.tendering": _view_tendering_role,
            "active.enquiries": _view_tendering_role,
            "active.auction": _view_tendering_role,
            "draft": _draft_view_role,
            "draft.pending": _draft_view_role + whitelist("features"),
            "draft.unsuccessful": _draft_view_role + whitelist("features", "unsuccessfulReason"),
            "active.awarded": _view_role,
            "unsuccessful": _view_role,
            "cancelled": _view_role,
            "view": _view_role,
            "active.qualification": _view_role,
            "complete": _view_role,
            "chronograph": _core_roles["chronograph"] + _procurement_method_details,
            "chronograph_view": _core_roles["chronograph_view"] + whitelist("agreements") + _procurement_method_details,
            "Administrator": _core_roles["Administrator"] + _procurement_method_details,
            "contracting": _core_roles["contracting"] + _procurement_method_details,
            "auction_post": _core_roles["auction_post"] + _procurement_method_details,
            "auction_patch": _core_roles["auction_patch"] + _procurement_method_details,
            "auction_view": _core_roles["auction_view"]
            - whitelist("minimalStep")
            + whitelist("serializable_minimalStep")
            + _procurement_method_details,
            "listing": _core_roles["listing"] + _procurement_method_details,
            "embedded": _core_roles["embedded"],
            "plain": _core_roles["plain"],
            "default": _core_roles["default"],
        }

    items = ListType(
        ModelType(Item, required=True), min_size=1, validators=[validate_items_uniq]
    )  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    value = ModelType(Value)  # The total estimated value of the procurement.
    enquiryPeriod = ModelType(
        PeriodEndRequired, required=False
    )  # The period during which enquiries may be made and will be answered.
    tenderPeriod = ModelType(
        PeriodEndRequired, required=False
    )  # The period when the tender is open for submissions. The end date is the closing date for tender submissions.
    hasEnquiries = BooleanType()  # A Yes/No field as to whether enquiries were part of tender process.
    awardPeriod = ModelType(Period)  # The date or period on which an award is anticipated to be made.
    numberOfBidders = IntType()  # The number of unique tenderers who participated in the tender
    bids = ListType(
        ModelType(Bid, required=True), default=list()
    )  # A list of all the companies who entered submissions for the tender.
    procuringEntity = ModelType(
        ProcuringEntity, required=True
    )  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    awards = ListType(ModelType(Award, required=True), default=list())
    contracts = ListType(ModelType(Contract, required=True), default=list())
    auctionPeriod = ModelType(TenderAuctionPeriod, default={})
    minimalStep = ModelType(Value, required=False)
    auctionUrl = URLType()
    cancellations = ListType(ModelType(Cancellation, required=True), default=list())
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    lots = ListType(
        ModelType(Lot, required=True), default=list(), validators=[validate_lots_uniq], min_size=1, max_size=1
    )
    guarantee = ModelType(Guarantee)
    status = StringType(
        choices=[
            "draft",
            "draft.pending",
            "draft.unsuccessful",
            "active.enquiries",
            "active.tendering",
            "active.auction",
            "active.qualification",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
        ],
        default="draft",
    )  # TODO Refactoring status
    agreements = ListType(ModelType(Agreement, required=True), default=list(), min_size=1, max_size=1)

    procurementMethod = StringType(choices=["open", "selective", "limited"], default="selective")
    procurementMethodType = StringType(default="closeFrameworkAgreementSelectionUA")
    unsuccessfulReason = ListType(StringType, serialize_when_none=False)
    procuring_entity_kinds = ["authority", "central", "defense", "general", "other", "social", "special"]

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == "Administrator":
            role = "Administrator"
        elif request.authenticated_role == "chronograph":
            role = "chronograph"
        elif request.authenticated_role == "auction":
            role = "auction_{}".format(request.method.lower())
        elif request.authenticated_role == "contracting":
            role = "contracting"
        elif request.authenticated_role == "agreement_selection":
            role = "edit_{}".format(request.authenticated_role)
        else:
            role = "edit_{}".format(request.context.status)
        return role

    def __acl__(self):
        acl = [(Allow, "{}_{}".format(i.owner, i.owner_token), "create_award_complaint") for i in self.bids]
        acl.extend(
            [
                (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_complaint"),
                (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_contract"),
                (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_contract_documents"),
                (Allow, "g:agreement_selection", "edit_agreement_selection"),
                (Allow, "g:agreement_selection", "edit_tender"),
                (Allow, "g:brokers", "create_cancellation_complaint")
            ]
        )
        self._acl_cancellation(acl)
        return acl

    def __local_roles__(self):
        roles = dict([("{}_{}".format(self.owner, self.owner_token), "tender_owner")])
        for i in self.bids:
            roles["{}_{}".format(i.owner, i.owner_token)] = "bid_owner"
        return roles

    # Non-required mainProcurementCategory
    def validate_mainProcurementCategory(self, data, value):
        pass

    # Not required milestones
    def validate_milestones(self, data, value):
        pass
