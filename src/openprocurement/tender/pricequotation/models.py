# -*- coding: utf-8 -*-
from uuid import uuid4
# from datetime import timedelta
# from barbecue import vnmax
from openprocurement.api.constants import TZ, CPV_ITEMS_CLASS_FROM
from openprocurement.api.models import\
    BusinessOrganization, CPVClassification, Guarantee
from openprocurement.api.models import Item as BaseItem
from openprocurement.api.models import\
    ListType, Period, Value, IsoDateTimeType
from openprocurement.api.models import\
    schematics_default_role, schematics_embedded_role
from openprocurement.api.utils import get_now
from openprocurement.api.validation import\
    validate_classification_id, validate_cpv_group, validate_items_uniq
from openprocurement.tender.core.models import (
    BaseAward,
    BaseCancellation,
    Model,
    Contract,
    Feature,
    PeriodEndRequired,
    ProcuringEntity,
    Parameter,
    Tender,
    BaseDocument
    )
from openprocurement.tender.core.models import (
    validate_features_uniq,
    Administrator_bid_role,
    view_bid_role,
    validate_parameters_uniq,
    get_tender
)
from openprocurement.tender.pricequotation.validation import\
    validate_bid_value
from openprocurement.tender.pricequotation.constants import PMT
from openprocurement.tender.pricequotation.interfaces\
    import IPriceQuotationTender
from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist, blacklist
from schematics.types import IntType, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.types import MD5Type
from zope.interface import implementer


class Document(BaseDocument):
    documentOf = StringType(
        required=True,
        choices=["tender", "item"],
        default="tender"
    )

    def validate_relatedItem(self, data, relatedItem):
        if not relatedItem and data.get("documentOf") in ["item"]:
            raise ValidationError(u"This field is required.")
        parent = data["__parent__"]
        if relatedItem and isinstance(parent, Model):
            tender = get_tender(parent)
            if data.get("documentOf") == "item" and relatedItem not in [i.id for i in tender.items if i]:
                raise ValidationError(u"relatedItem should be one of items")



class Award(BaseAward):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """

    class Options:
        roles = {
            "create": blacklist("id", "status", "date", "documents"),
            "edit": whitelist(
                "status", "title", "title_en", "title_ru", "description", "description_en", "description_ru"
            ),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
            "Administrator": whitelist("complaintPeriod"),
        }

    bid_id = MD5Type(required=True)


class BidOffer(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    relatedItem = MD5Type(required=True)
    requirementsResponse = StringType(required=True)


class Bid(Model):
    class Options:
        roles = {
            "Administrator": Administrator_bid_role,
            "embedded": view_bid_role,
            "view": view_bid_role,
            "create": whitelist(
                "value",
                "status",
                "tenderers",
                "parameters",
                "documents"
            ),
            "edit": whitelist("value", "status", "tenderers", "parameters"),
            "active.tendering": whitelist(),
            "active.qualification": view_bid_role,
            "active.awarded": view_bid_role,
            "complete": view_bid_role,
            "unsuccessful": view_bid_role,
            "cancelled": view_bid_role,
        }

    def __local_roles__(self):
        return dict([("{}_{}".format(self.owner, self.owner_token),
                      "bid_owner")])

    tenderers = ListType(
        ModelType(BusinessOrganization, required=True),
        required=True,
        min_size=1,
        max_size=1
    )
    parameters = ListType(
        ModelType(Parameter, required=True),
        default=list(),
        validators=[validate_parameters_uniq]
    )
    date = IsoDateTimeType(default=get_now)
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(choices=["active", "draft"], default="active")
    value = ModelType(Value)
    documents = ListType(ModelType(Document, required=True), default=list())
    owner_token = StringType()
    transfer_token = StringType()
    owner = StringType()
    # TODO: 
    # offers = ListType(
    #     ModelType(BidOffer, required=True),
    #     required=True,
    #     min_size=1,
    #     validators=[validate_items_uniq],
    # )

    __name__ = ""

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.

        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [k for k in data.keys() if k != "value" and data[k] is None]
        for k in del_keys:
            del data[k]

        self._data.update(data)
        return self

    def __acl__(self):
        return [
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_bid")
        ]

    def validate_value(self, data, value):
        parent = data["__parent__"]
        if isinstance(parent, Model):
            validate_bid_value(parent, value)

    def validate_parameters(self, data, parameters):
        parent = data["__parent__"]
        if isinstance(parent, Model):
            tender = parent
            if not parameters and tender.features:
                raise ValidationError(u"This field is required.")
            elif set([i["code"] for i in parameters]) != set([
                    i.code for i in (tender.features or [])
            ]):
                raise ValidationError(u"All features parameters is required.")

# TODO: relatedLot
class Cancellation(BaseCancellation):
    def validate_relatedLot(self, data, relatedLot):
        pass


class ShortlistedFirm(BusinessOrganization):
    id = StringType()
    status = StringType()


class Item(BaseItem):
    """A good, service, or work to be contracted."""
    classification = ModelType(CPVClassification)


@implementer(IPriceQuotationTender)
class PriceQuotationTender(Tender):
    """
    Data regarding tender process - publicly inviting prospective contractors
    to submit bids for evaluation and selecting a winner or winners.
    """

    class Options:
        namespace = "Tender"
        _core_roles = Tender.Options.roles
        # without _serializable_fields they won't be calculated
        # (even though serialized_name is in the role)
        _serializable_fields = whitelist(
            "tender_guarantee",
            "tender_value",
            "tender_minimalStep"
        )
        _edit_fields = _serializable_fields + whitelist(
            "next_check",
            "numberOfBidders",
            "features",
            "items",
            "tenderPeriod",
            "procuringEntity",
            "guarantee",
            "value",
            "minimalStep",
        )
        _edit_role = _core_roles["edit"] \
            + _edit_fields + whitelist(
                "contracts",
                "numberOfBids",
                "status",
                "profile"
            )
        _edit_pq_bot_role = whitelist("items", "shortlistedFirms", "status")
        _view_tendering_role = (
            _core_roles["view"]
            + _edit_fields
            + whitelist(
                "awards",
                "awardPeriod",
                "cancellations",
                "contracts",
                "profile",
                "shortlistedFirms"
            )
        )
        _view_role = _view_tendering_role + whitelist("bids", "numberOfBids")
        _all_forbidden = whitelist()
        roles = {
            "create": _core_roles["create"] + _edit_role + whitelist("lots"),
            "edit": _edit_role,
            "edit_draft": _edit_role,
            "edit_draft.unsuccessful": _edit_role,
            "edit_draft.publishing": _all_forbidden,
            "edit_active.tendering": _all_forbidden,
            "edit_active.qualification": _all_forbidden,
            "edit_active.awarded": _all_forbidden,
            "edit_complete": _all_forbidden,
            "edit_unsuccessful": _all_forbidden,
            "edit_cancelled": _all_forbidden,
            "draft": _view_tendering_role,
            "draft.unsuccessful": _view_tendering_role,
            "draft.publishing": _view_tendering_role,
            "active.tendering": _view_tendering_role,
            "view": _view_role,
            "active.qualification": _view_role,
            "active.awarded": _view_role,
            "complete": _view_role,
            "unsuccessful": _view_role,
            "cancelled": _view_role,
            "chronograph": _core_roles["chronograph"],
            "chronograph_view": _core_roles["chronograph_view"],
            "Administrator": _core_roles["Administrator"],
            "plain": _core_roles["plain"],
            "listing": _core_roles["listing"],
            "contracting": _core_roles["contracting"],
            "default": _core_roles["default"],
            "bots": _edit_pq_bot_role,
        }

    status = StringType(choices=["draft",
                                 "draft.publishing",
                                 "draft.unsuccessful",
                                 "active.tendering",
                                 "active.qualification",
                                 "active.awarded",
                                 "complete",
                                 "cancelled",
                                 "unsuccessful"],
                        default="draft")

    # The goods and services to be purchased,
    # broken into line items wherever possible.
    # Items should not be duplicated, but a quantity of 2 specified instead.
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq],
    )
    # The total estimated value of the procurement.
    value = ModelType(Value, required=True)
    # The period when the tender is open for submissions.
    # The end date is the closing date for tender submissions.
    tenderPeriod = ModelType(
        PeriodEndRequired, required=True
    )
    # The date or period on which an award is anticipated to be made.
    awardPeriod = ModelType(Period)
    # The number of unique tenderers who participated in the tender
    numberOfBidders = IntType()
    # A list of all the companies who entered submissions for the tender.
    bids = ListType(
        ModelType(Bid, required=True), default=list()
    )
    # The entity managing the procurement,
    # which may be different from the buyer
    # who is paying / using the items being procured.
    procuringEntity = ModelType(ProcuringEntity, required=True)
    awards = ListType(ModelType(Award, required=True), default=list())
    contracts = ListType(ModelType(Contract, required=True), default=list())
    cancellations = ListType(
        ModelType(Cancellation, required=True),
        default=list()
    )
    features = ListType(
        ModelType(Feature, required=True),
        validators=[validate_features_uniq]
    )
    guarantee = ModelType(Guarantee)
    procurementMethodType = StringType(default=PMT)
    profile = StringType()
    shortlistedFirms = ListType(ModelType(ShortlistedFirm), default=list())

    procuring_entity_kinds = ["general", "special",
                              "defense", "central", "other"]
    block_complaint_status = ["answered", "pending"]

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role in\
           ("Administrator", "chronograph", "contracting", "bots"):
            role = request.authenticated_role
        elif request.authenticated_role == "auction":
            role = "auction_{}".format(request.method.lower())
        else:
            role = "edit_{}".format(request.context.status)
        return role

    @serializable(serialize_when_none=False)
    def next_check(self):
        checks = []
        if self.status == "active.tendering" and self.tenderPeriod.endDate:
            checks.append(self.tenderPeriod.endDate.astimezone(TZ))

        if self.status.startswith("active"):
            for award in self.awards:
                if award.status == "active" and not\
                   any([i.awardID == award.id for i in self.contracts]):
                    checks.append(award.date)
        return min(checks).isoformat() if checks else None

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        return len(self.bids)

    def validate_items(self, data, items):
        if data["status"] in ("draft", "draft.publishing", "draft.unsuccessful"):
            return
        cpv_336_group = items[0].classification.id[:3] == "336"\
            if items else False
        cpv_validate_from = data.get("revisions")[0].date\
            if data.get("revisions") else get_now()
        if (
            not cpv_336_group
            and cpv_validate_from > CPV_ITEMS_CLASS_FROM
            and items
            and len(set([i.classification.id[:4] for i in items])) != 1
        ):
            raise ValidationError(u"CPV class of items should be identical")
        else:
            validate_cpv_group(items)
        validate_classification_id(items)

    def validate_awardPeriod(self, data, period):
        if (
            period
            and period.startDate
            and data.get("tenderPeriod")
            and data.get("tenderPeriod").endDate
            and period.startDate < data.get("tenderPeriod").endDate
        ):
            raise ValidationError(u"period should begin after tenderPeriod")
