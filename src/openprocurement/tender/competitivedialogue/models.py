# -*- coding: utf-8 -*-
from schematics.types import StringType, FloatType
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist, blacklist
from zope.interface import implementer
from pyramid.security import Allow
from schematics.types.compound import ModelType

from openprocurement.api.auth import ACCR_3, ACCR_COMPETITIVE, ACCR_5
from openprocurement.api.models import (
    Model,
    Identifier,
    schematics_default_role,
    schematics_embedded_role,
    ListType,
    SifterListType,
    BooleanType,
    Value as BaseValue,
    CPVClassification as BaseCPVClassification,
)
from openprocurement.api.utils import get_now
from openprocurement.api.validation import validate_cpv_group, validate_items_uniq
from openprocurement.tender.core.models import (
    ITender,
    validate_features_uniq,
    validate_values_uniq,
    Feature as BaseFeature,
    FeatureValue as BaseFeatureValue,
    ProcuringEntity as BaseProcuringEntity,
    get_tender,
    PeriodStartEndRequired,
    validate_lots_uniq,
    Lot as BaseLotUA,
    EUConfidentialDocument,
)
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.openua.models import Item as BaseUAItem, Tender as BaseTenderUA
from openprocurement.tender.openua.constants import TENDER_PERIOD as TENDERING_DURATION_UA
from openprocurement.tender.openeu.models import (
    Administrator_bid_role,
    view_bid_role,
    embedded_lot_role,
    default_lot_role,
    Lot as BaseLotEU,
    Item as BaseEUItem,
    LotValue as BaseLotValueEU,
    Tender as BaseTenderEU,
    Bid as BidEU,
)
from openprocurement.tender.openeu.constants import TENDERING_DURATION as TENDERING_DURATION_EU
from openprocurement.tender.competitivedialogue.utils import validate_features_custom_weight
from openprocurement.tender.competitivedialogue.constants import (
    CD_UA_TYPE,
    CD_EU_TYPE,
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
    STAGE2_STATUS,
    FEATURES_MAX_SUM,
)


class ICDEUTender(ITender):
    """ Marker interface for Competitive Dialogue EU tenders """


class ICDUATender(ITender):
    """ Marker interface for Competitive Dialogue UA tenders """


class ICDEUStage2Tender(ITender):
    """ Marker interface for Competitive Dialogue EU Stage 2 tenders """


class ICDUAStage2Tender(ITender):
    """ Marker interface for Competitive Dialogue UA Stage 2 tenders """


class Document(EUConfidentialDocument):
    isDescriptionDecision = BooleanType(default=False)

    def validate_confidentialityRationale(self, data, val):
        if data["confidentiality"] != "public" and not data["isDescriptionDecision"]:
            if not val:
                raise ValidationError(u"confidentialityRationale is required")
            elif len(val) < 30:
                raise ValidationError(u"confidentialityRationale should contain at least 30 characters")


class LotValue(BaseLotValueEU):
    class Options:
        roles = {
            "create": whitelist("relatedLot", "subcontractingDetails"),
            "edit": whitelist("relatedLot", "subcontractingDetails"),
            "view": (schematics_default_role + blacklist("value")),
        }

    value = ModelType(BaseValue, required=False)

    def validate_value(self, *args, **kwargs):
        pass  # remove validation


view_bid_role_stage1 = view_bid_role + blacklist("value")


class Bid(BidEU):
    class Options:
        roles = {
            "Administrator": Administrator_bid_role,
            "embedded": view_bid_role_stage1,
            "view": view_bid_role_stage1,
            "create": whitelist(
                "tenderers",
                "lotValues",
                "status",
                "selfQualified",
                "selfEligible",
                "subcontractingDetails",
                "documents",
            ),
            "edit": whitelist("tenderers", "lotValues", "status", "subcontractingDetails"),
            "active.enquiries": whitelist(),
            "active.tendering": whitelist(),
            "active.pre-qualification": whitelist("id", "status", "documents", "tenderers"),
            "active.pre-qualification.stand-still": whitelist("id", "status", "documents", "tenderers"),
            "active.auction": whitelist("id", "status", "documents", "tenderers"),
            "active.stage2.pending": whitelist("id", "status", "documents", "tenderers"),
            "active.stage2.waiting": whitelist("id", "status", "documents", "tenderers"),
            "active.qualification": view_bid_role,
            "complete": view_bid_role_stage1,
            "unsuccessful": view_bid_role_stage1,
            "cancelled": view_bid_role_stage1,
            "invalid": whitelist("id", "status"),
            "deleted": whitelist("id", "status"),
        }

    documents = ListType(ModelType(Document, required=True), default=list())
    value = None
    lotValues = ListType(ModelType(LotValue, required=True), default=list())

    def validate_value(self, *args, **kwargs):
        pass  # remove validation on stage 1

    def validate_parameters(self, data, parameters):
        pass  # remove validation on stage 1


class FeatureValue(BaseFeatureValue):
    value = FloatType(required=True, min_value=0.0, max_value=FEATURES_MAX_SUM)


class Feature(BaseFeature):
    enum = ListType(
        ModelType(FeatureValue, required=True), default=list(), min_size=1, validators=[validate_values_uniq]
    )


lot_roles = {
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
    "chronograph": whitelist("id", "auctionPeriod"),
    "chronograph_view": whitelist("id", "auctionPeriod", "numberOfBids", "status"),
}


class Lot(BaseLotEU):
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
            "view": (default_lot_role + blacklist("auctionPeriod")),
            "default": (default_lot_role + blacklist("auctionPeriod")),
            "chronograph": whitelist("id"),
            "chronograph_view": whitelist("id", "numberOfBids", "status"),
        }


LotStage1 = Lot


@implementer(ICDEUTender)
class CompetitiveDialogEU(BaseTenderEU):
    procurementMethodType = StringType(default=CD_EU_TYPE)
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.stage2.pending",
            "active.stage2.waiting",
            "complete",
            "cancelled",
            "unsuccessful",
        ],
        default="active.tendering",
    )
    # A list of all the companies who entered submissions for the tender.
    bids = SifterListType(
        ModelType(Bid, required=True), default=list(), filter_by="status", filter_in_values=["invalid", "deleted"]
    )
    TenderID = StringType(required=False)
    stage2TenderID = StringType(required=False)
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    lots = ListType(ModelType(Lot, required=True), default=list(), validators=[validate_lots_uniq])
    items = ListType(
        ModelType(BaseEUItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq],
    )
    mainProcurementCategory = StringType(choices=["services", "works"])

    class Options:
        namespace = "Tender"
        _parent_roles = BaseTenderEU.Options.roles

        _stage2_id = whitelist("stage2TenderID")
        _pre_qualifications_role = _parent_roles["active.pre-qualification"] + _stage2_id - whitelist("auctionPeriod")
        _view_role = _parent_roles["view"] + _stage2_id - whitelist("auctionPeriod")
        _tendering_role = _parent_roles["active.tendering"] + _stage2_id - whitelist("auctionPeriod")

        roles = {
            "create": _parent_roles["create"],
            "active.pre-qualification": _pre_qualifications_role,
            "active.pre-qualification.stand-still": _pre_qualifications_role,
            "active.stage2.pending": _pre_qualifications_role,
            "active.stage2.waiting": _pre_qualifications_role,
            "edit_active.stage2.pending": whitelist("status"),
            "draft": _tendering_role,
            "active.tendering": _tendering_role,
            "complete": _view_role,
            "unsuccessful": _view_role,
            "view": _view_role,
            "cancelled": _view_role,
            "chronograph": _parent_roles["chronograph"],
            "chronograph_view": _parent_roles["chronograph_view"],
            "Administrator": _parent_roles["Administrator"],
            "default": _parent_roles["default"],
            "plain": _parent_roles["plain"],
            "contracting": _parent_roles["contracting"],
            "listing": _parent_roles["listing"],
            "competitive_dialogue": whitelist("status", "stage2TenderID"),
        }

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == "Administrator":
            role = "Administrator"
        elif request.authenticated_role == "chronograph":
            role = "chronograph"
        elif request.authenticated_role == "competitive_dialogue":
            role = "competitive_dialogue"
        else:
            role = "edit_{}".format(request.context.status)
        return role

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
                (Allow, "g:competitive_dialogue", "extract_credentials"),
                (Allow, "g:competitive_dialogue", "edit_tender"),
                (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_cancellation"),
            ]
        )

        self._acl_cancellation_complaint(acl)
        return acl

    def validate_features(self, data, features):
        validate_features_custom_weight(self, data, features, FEATURES_MAX_SUM)


class LotId(Model):
    id = StringType()

    def validate_id(self, data, lot_id):
        parent = data["__parent__"]
        if lot_id and isinstance(parent, Model) and lot_id not in [lot.id for lot in get_tender(parent).lots if lot]:
            raise ValidationError(u"id should be one of lots")


class Firms(Model):
    identifier = ModelType(Identifier, required=True)
    name = StringType(required=True)
    lots = ListType(ModelType(LotId, required=True), default=list())


@implementer(ICDUATender)
class CompetitiveDialogUA(CompetitiveDialogEU):
    procurementMethodType = StringType(default=CD_UA_TYPE)
    title_en = StringType()
    items = ListType(
        ModelType(BaseUAItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq],
    )
    procuringEntity = ModelType(BaseProcuringEntity, required=True)
    stage2TenderID = StringType(required=False)
    mainProcurementCategory = StringType(choices=["services", "works"])


# stage 2 models


def init_PeriodStartEndRequired(tendering_duration):
    def wrapper():
        return PeriodStartEndRequired(
            {"startDate": get_now(), "endDate": calculate_tender_business_date(get_now(), tendering_duration)}
        )

    return wrapper


def stage2__acl__(obj):
    acl = [
        (Allow, "{}_{}".format(obj.owner, obj.dialogue_token), "generate_credentials"),
        (Allow, "{}_{}".format(obj.owner, obj.owner_token), "edit_complaint"),
        (Allow, "{}_{}".format(obj.owner, obj.owner_token), "edit_contract"),
        (Allow, "{}_{}".format(obj.owner, obj.owner_token), "upload_contract_documents"),
        (Allow, "g:competitive_dialogue", "edit_tender"),
        (Allow, "g:competitive_dialogue", "edit_cancellation")
    ]
    acl.extend(
        [
            (Allow, "{}_{}".format(i.owner, i.owner_token), "create_qualification_complaint")
            for i in obj.bids
            if i.status in ["active", "unsuccessful"]
        ]
    )
    acl.extend(
        [
            (Allow, "{}_{}".format(i.owner, i.owner_token), "create_award_complaint")
            for i in obj.bids
            if i.status == "active"
        ]
    )

    return acl


lot_stage2_roles = {
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
    "edit": whitelist(),
    "embedded": embedded_lot_role,
    "view": default_lot_role,
    "default": default_lot_role,
    "auction_view": default_lot_role,
    "auction_patch": whitelist("id", "auctionUrl"),
    "chronograph": whitelist("id", "auctionPeriod"),
    "chronograph_view": whitelist("id", "auctionPeriod", "numberOfBids", "status"),
}


class Lot(BaseLotUA):
    class Options:
        roles = lot_stage2_roles


LotStage2UA = Lot


class Lot(BaseLotEU):
    class Options:
        roles = lot_stage2_roles


LotStage2EU = Lot


class CPVClassification(BaseCPVClassification):
    def validate_scheme(self, data, scheme):
        pass


class Item(BaseEUItem):
    class Options:
        roles = {"edit_active.tendering": whitelist("deliveryDate")}

    classification = ModelType(CPVClassification, required=True)


ItemStage2EU = Item


class Item(BaseUAItem):
    class Options:
        roles = {"edit_active.tendering": whitelist("deliveryDate")}

    classification = ModelType(CPVClassification, required=True)


ItemStage2UA = Item


class Award(BaseTenderEU.awards.model_class):

    items = ListType(ModelType(ItemStage2EU, required=True))


class Contract(BaseTenderEU.contracts.model_class):

    items = ListType(ModelType(ItemStage2EU, required=True))


@implementer(ICDEUStage2Tender)
class TenderStage2EU(BaseTenderEU):
    procurementMethodType = StringType(default=STAGE_2_EU_TYPE)
    dialogue_token = StringType(required=True)
    dialogueID = StringType()
    shortlistedFirms = ListType(ModelType(Firms, required=True), min_size=3, required=True)
    tenderPeriod = ModelType(
        PeriodStartEndRequired, required=False, default=init_PeriodStartEndRequired(TENDERING_DURATION_EU)
    )
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
            STAGE2_STATUS,
        ],
        default="active.tendering",
    )
    lots = ListType(ModelType(LotStage2EU, required=True), default=list(), validators=[validate_lots_uniq])
    procurementMethod = StringType(choices=["open", "selective", "limited"], default="selective")

    # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    items = ListType(
        ModelType(ItemStage2EU, required=True),
        required=True,
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq],
    )
    awards = ListType(ModelType(Award, required=True), default=list())
    contracts = ListType(ModelType(Contract, required=True), default=list())
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])

    create_accreditations = (ACCR_COMPETITIVE,)
    central_accreditations = (ACCR_COMPETITIVE, ACCR_5)
    transfer_accreditations = (ACCR_3, ACCR_5)

    class Options:
        namespace = "Tender"
        _parent_roles = BaseTenderEU.Options.roles

        _stage2_fields = whitelist("shortlistedFirms", "dialogueID")  # not covered (in view roles)
        _pre_qualifications_role = _parent_roles["active.pre-qualification"] + _stage2_fields
        _view_role = _parent_roles["view"] - whitelist("auctionPeriod") + _stage2_fields

        _tendering_role = _parent_roles["active.tendering"] + _stage2_fields
        _all_forbidden = whitelist()

        roles = {
            # competitive bridge creates stage2 tenders and set owners to corresponding brokers
            # also tenderID is set as "{stage1.tenderID}.2"
            "create": _parent_roles["create"]
            + _stage2_fields
            - whitelist("tenderPeriod")
            + whitelist("dialogue_token", "owner", "tenderID"),
            "edit": whitelist("tenderPeriod"),
            "edit_draft": whitelist("status"),  # only bridge must change only status
            "edit_active.pre-qualification": whitelist("status"),
            "edit_" + STAGE2_STATUS: whitelist("tenderPeriod", "status"),
            "edit_active.tendering": whitelist("tenderPeriod", "items"),
            "edit_active.pre-qualification.stand-still": _all_forbidden,
            "edit_active.auction": _all_forbidden,
            "edit_active.qualification": _all_forbidden,
            "edit_active.awarded": _all_forbidden,
            "edit_complete": _all_forbidden,
            "edit_unsuccessful": _all_forbidden,
            "edit_cancelled": _all_forbidden,
            "draft": _tendering_role,
            "draft.stage2": _tendering_role,
            "active.tendering": _tendering_role,
            "active.pre-qualification": _pre_qualifications_role,
            "active.pre-qualification.stand-still": _pre_qualifications_role,
            "active.auction": _pre_qualifications_role,
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
            "competitive_dialogue": CompetitiveDialogEU.Options.roles["competitive_dialogue"],
        }

    def __acl__(self):
        acl = stage2__acl__(self)
        self._acl_cancellation_complaint(acl)
        return acl

    def validate_features(self, data, features):
        validate_features_custom_weight(self, data, features, FEATURES_MAX_SUM)

    # Non-required mainProcurementCategory
    def validate_mainProcurementCategory(self, data, value):
        pass

    # Not required milestones
    def validate_milestones(self, data, value):
        pass


class Award(BaseTenderUA.awards.model_class):

    items = ListType(ModelType(ItemStage2UA, required=True))


class Contract(BaseTenderUA.contracts.model_class):

    items = ListType(ModelType(ItemStage2UA, required=True))


@implementer(ICDUAStage2Tender)
class TenderStage2UA(BaseTenderUA):
    procurementMethodType = StringType(default=STAGE_2_UA_TYPE)
    dialogue_token = StringType(required=True)
    dialogueID = StringType()
    shortlistedFirms = ListType(ModelType(Firms, required=True), min_size=3, required=True)
    tenderPeriod = ModelType(
        PeriodStartEndRequired, required=False, default=init_PeriodStartEndRequired(TENDERING_DURATION_UA)
    )
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
            STAGE2_STATUS,
        ],
        default="active.tendering",
    )
    lots = ListType(ModelType(LotStage2UA, required=True), default=list(), validators=[validate_lots_uniq])
    items = ListType(
        ModelType(ItemStage2UA, required=True),
        required=True,
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq],
    )
    awards = ListType(ModelType(Award, required=True), default=list())
    contracts = ListType(ModelType(Contract, required=True), default=list())
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    procurementMethod = StringType(choices=["open", "selective", "limited"], default="selective")

    create_accreditations = (ACCR_COMPETITIVE,)
    central_accreditations = (ACCR_COMPETITIVE, ACCR_5)
    transfer_accreditations = (ACCR_3, ACCR_5)

    class Options(TenderStage2EU.Options):
        pass

    def __acl__(self):
        acl = stage2__acl__(self)
        self._acl_cancellation_complaint(acl)
        return acl

    def validate_features(self, data, features):
        validate_features_custom_weight(self, data, features, FEATURES_MAX_SUM)

    # Non-required mainProcurementCategory
    def validate_mainProcurementCategory(self, data, value):
        pass

    # Not required milestones
    def validate_milestones(self, data, value):
        pass
