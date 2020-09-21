# -*- coding: utf-8 -*-
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist
from schematics.types import IntType, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from pyramid.security import Allow
from zope.interface import implementer
from openprocurement.api.constants import TZ
from openprocurement.api.models import (
    BusinessOrganization,
    CPVClassification,
    Guarantee,
    IsoDateTimeType,
)
from openprocurement.api.models import Item as BaseItem
from openprocurement.api.models import ListType, Period, Value
from openprocurement.api.utils import get_now
from openprocurement.api.validation import (
    validate_classification_id,
    validate_cpv_group,
    validate_items_uniq,
)
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.core.models import (
    Contract as BaseContract,
    PeriodEndRequired,
    ProcuringEntity,
    Tender,
    Model,
)
from openprocurement.tender.openua.validation import validate_tender_period_duration
from openprocurement.tender.pricequotation.constants import (
    PMT,
    QUALIFICATION_DURATION,
    PQ_KINDS,
    PROFILE_PATTERN,
    TENDERING_DURATION,
)
from openprocurement.tender.pricequotation.interfaces import IPriceQuotationTender

from openprocurement.tender.pricequotation.models import (
    Cancellation,
    Bid,
    Document,
    Award,
)
from openprocurement.tender.pricequotation.models.criterion import Criterion


class ShortlistedFirm(BusinessOrganization):
    id = StringType()
    status = StringType()


class Item(BaseItem):
    class Options:
        roles = {
            'create': whitelist(
                'id',
                'description',
                'description_en',
                'description_ru',
                'quantity',
                'deliveryDate',
                'deliveryAddress',
                'deliveryLocation'
            ),
            'edit': whitelist(
                'description',
                'description_en',
                'description_ru',
                'quantity',
                'deliveryDate',
                'deliveryAddress',
                'deliveryLocation',
            ),
            'bots': whitelist(
                'classification',
                'additionalClassifications',
                'unit'
            ),
            "edit_contract": whitelist("unit")
        }

    """A good, service, or work to be contracted."""
    classification = ModelType(CPVClassification)


class Contract(BaseContract):
    documents = ListType(ModelType(Document, required=True), default=list())

    def validate_dateSigned(self, data, value):
        parent = data["__parent__"]
        if value and isinstance(parent, Model):
            if value > get_now():
                raise ValidationError(u"Contract signature date can't be in the future")



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
            "items",
            "tenderPeriod",
            "procuringEntity",
            "guarantee",
            "minimalStep",
        )
        _edit_role = _core_roles["edit"] \
            + _edit_fields + whitelist(
                "contracts",
                "numberOfBids",
                "status",
                "value",
                "profile"
            )
        _create_role = _core_roles["create"] \
                       + _core_roles["edit"] \
                       + _edit_fields \
                       + whitelist("contracts",
                                   "numberOfBids",
                                   "value",
                                   "profile")
        _edit_pq_bot_role = whitelist(
            "items", "shortlistedFirms",
            "status", "criteria", "value", "unsuccessfulReason"
        )
        _view_tendering_role = (
            _core_roles["view"]
            + _edit_fields
            + whitelist(
                "awards",
                'value',
                "awardPeriod",
                "cancellations",
                "contracts",
                "profile",
                "shortlistedFirms",
                "criteria",
                "noticePublicationDate",
                "unsuccessfulReason"
            )
        )
        _view_role = _view_tendering_role + whitelist("bids", "numberOfBids")
        _all_forbidden = whitelist()
        roles = {
            "create": _create_role,
            "edit": _edit_role,
            "edit_draft": _edit_role,
            "edit_draft.unsuccessful": _edit_role,
            "edit_draft.publishing": _edit_pq_bot_role,
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
    documents = ListType(
        ModelType(Document, required=True), default=list()
    )  # All documents and attachments related to the tender.
    guarantee = ModelType(Guarantee)
    procurementMethod = StringType(
        choices=["selective"], default="selective"
    )
    procurementMethodType = StringType(default=PMT)
    profile = StringType(required=True)
    shortlistedFirms = ListType(ModelType(ShortlistedFirm), default=list())
    criteria = ListType(ModelType(Criterion), default=list())
    noticePublicationDate = IsoDateTimeType()
    unsuccessfulReason = ListType(StringType)

    procuring_entity_kinds = PQ_KINDS

    def validate_buyers(self, data, value):
        pass

    def validate_milestones(self, data, value):
        # a hack to avoid duplicating all bese model fields
        if value:
            raise ValidationError("Milestones are not applicable to pricequotation")

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role in\
           ("Administrator", "chronograph", "contracting", "bots"):
            role = request.authenticated_role
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
                if award.status == 'pending':
                    checks.append(
                        calculate_tender_business_date(award.date, QUALIFICATION_DURATION, self)
                    )
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
        if not all((i.classification for i in items)):
            return
        cpv_336_group = items[0].classification.id[:3] == "336"\
            if items else False
        if (
            not cpv_336_group
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

    def validate_tenderPeriod(self, data, period):
        if period and period.startDate and period.endDate:
            validate_tender_period_duration(data, period, TENDERING_DURATION, working_days=True)


    def validate_profile(self, data, profile):
        result = PROFILE_PATTERN.findall(profile)
        if len(result) != 1:
            raise ValidationError(u"The profile value doesn't match id pattern")

    def __local_roles__(self):
        roles = dict([("{}_{}".format(self.owner, self.owner_token), "tender_owner")])
        for i in self.bids:
            roles["{}_{}".format(i.owner, i.owner_token)] = "bid_owner"
        return roles

    def _acl_contract(self, acl):
        acl.extend([
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_contract"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_contract_documents"),
        ])

    def _acl_cancellation(self, acl):
        acl.extend([
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_cancellation"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_tender"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_tender_documents"),
        ])

    def __acl__(self):
        acl = [
            (Allow, "g:bots", "upload_award_documents"),
        ]
        self._acl_cancellation(acl)
        self._acl_contract(acl)
        return acl
