# -*- coding: utf-8 -*-
from zope.interface import implementer
from pyramid.security import Allow
from schematics.transforms import whitelist, blacklist
from schematics.types import StringType, MD5Type, BooleanType, BaseType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.exceptions import ValidationError
from openprocurement.api.constants import (
    MILESTONES_VALIDATION_FROM,
    QUICK_CAUSE_REQUIRED_FROM,
    TZ,
)
from openprocurement.api.auth import ACCR_1, ACCR_2, ACCR_3, ACCR_4, ACCR_5
from openprocurement.api.utils import get_now, get_root, get_first_revision_date
from openprocurement.api.models import schematics_default_role, schematics_embedded_role
from openprocurement.api.models import ListType, Period, Model
from openprocurement.api.models import Value as BaseValue
from openprocurement.api.models import Unit as BaseUnit
from openprocurement.api.validation import validate_cpv_group, validate_items_uniq, validate_classification_id
from openprocurement.tender.core.models import (
    embedded_lot_role,
    default_lot_role,
    validate_lots_uniq,
    BaseLot,
    BaseAward,
    Document,
    BaseTender,
    ITender,
    Contract as BaseContract,
    ProcuringEntity as BaseProcuringEntity,
)

from openprocurement.tender.core.utils import extend_next_check_by_complaint_period_ends
from openprocurement.tender.openua.models import (
    Complaint as BaseComplaint,
    Item,
    Tender as OpenUATender,
    Cancellation as BaseCancellation
)


class IReportingTender(ITender):
    """ Reporting Tender marker interface """


class INegotiationTender(ITender):
    """ Negotiation Tender marker interface """


class INegotiationQuickTender(INegotiationTender):
    """ Negotiation Quick Tender marker interface """


class Value(BaseValue):
    currency = StringType(max_length=3, min_length=3)
    valueAddedTaxIncluded = BooleanType()

    @serializable(serialized_name="currency", serialize_when_none=False)
    def unit_currency(self):
        if self.currency is not None:
            return self.currency

        context = self.__parent__ if isinstance(self.__parent__, Model) else {}
        while isinstance(context.__parent__, Model):
            context = context.__parent__
            if isinstance(context, BaseContract):
                break

        value = context.get("value", {})
        return value.get("currency", None)

    @serializable(serialized_name="valueAddedTaxIncluded", serialize_when_none=False)
    def unit_valueAddedTaxIncluded(self):
        if self.valueAddedTaxIncluded is not None:
            return self.valueAddedTaxIncluded

        context = self.__parent__ if isinstance(self.__parent__, Model) else {}
        while isinstance(context.__parent__, Model):
            context = context.__parent__
            if isinstance(context, BaseContract):
                break

        value = context.get("value", {})
        return value.get("valueAddedTaxIncluded", None)


class Unit(BaseUnit):
    value = ModelType(Value)


class BaseItem(Item):
    unit = ModelType(Unit)

    class Options:
        roles = {"edit_contract": whitelist("unit")}


class Item(BaseItem):
    def validate_relatedLot(self, data, relatedLot):
        if relatedLot and isinstance(data["__parent__"], Model):
            raise ValidationError(u"This option is not available")


class Complaint(BaseComplaint):
    pass


class Contract(BaseContract):
    items = ListType(ModelType(Item, required=True))

    class Options:
        roles = {
            "edit": whitelist(),
            "edit_contract": blacklist("id", "documents", "date", "awardID", "suppliers", "contractID"),
        }

    def validate_dateSigned(self, data, value):
        if value and value > get_now():
            raise ValidationError(u"Contract signature date can't be in the future")

    def get_role(self):
        root = self.get_root()
        request = root.request
        role = "edit"
        if request.authenticated_role == "tender_owner":
            role = "edit_contract"
        return role


Unit = BaseUnit
Value = BaseValue


award_edit_role = blacklist("id", "items", "date", "documents", "complaints", "complaintPeriod")
award_create_role = blacklist("id", "status", "items", "date", "documents", "complaints", "complaintPeriod")
award_create_reporting_role = award_create_role + blacklist("qualified")
award_edit_reporting_role = award_edit_role + blacklist("qualified")


class Award(BaseAward):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """

    class Options:
        roles = {
            "create": award_create_reporting_role,
            "edit": award_edit_reporting_role,
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
            "Administrator": whitelist("complaintPeriod"),
        }

    qualified = BooleanType()
    items = ListType(ModelType(Item, required=True))
    documents = ListType(ModelType(Document, required=True), default=list())
    complaints = ListType(ModelType(Complaint, required=True), default=list())
    complaintPeriod = ModelType(Period)


ReportingAward = Award


class Cancellation(BaseCancellation):
    class Options:
        roles = {
            "create": whitelist("reason", "status", "reasonType", "cancellationOf", "relatedLot"),
            "edit": whitelist("status", "reasonType"),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }

    def validate_relatedLot(self, data, relatedLot):
        if not relatedLot and data.get("cancellationOf") == "lot":
            raise ValidationError(u"This field is required.")
        if (
            relatedLot
            and isinstance(data["__parent__"], Model)
            and relatedLot not in [i.id for i in data["__parent__"].get("lots", [])]
        ):
            raise ValidationError(u"relatedLot should be one of lots")

    def validate_cancellationOf(self, data, cancellationOf):
        if (
            isinstance(data["__parent__"], Model)
            and cancellationOf == "lot"
            and not hasattr(data["__parent__"], "lots")
        ):
            raise ValidationError(
                u'Lot cancellation can not be submitted, since "multiple lots" option is not available for this type of tender.'
            )


class ReportingCancellation(Cancellation):
    class Options:
        namespace = "Cancellation"
        roles = Cancellation.Options.roles

    _after_release_status_choices = ["draft", "unsuccessful", "active"]


class NegotiationCancellation(Cancellation):
    class Options:
        namespace = "Cancellation"
        roles = Cancellation.Options.roles

    _after_release_reasonType_choices = ["noObjectiveness", "unFixable", "noDemand", "expensesCut", "dateViolation"]


class ProcuringEntity(BaseProcuringEntity):
    class Options:
        roles = {"edit_active": schematics_default_role + blacklist("kind")}


@implementer(ITender)
class ReportingTender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors
       to submit bids for evaluation and selecting a winner or winners.
    """

    class Options:
        namespace = "Tender"
        _parent_roles = BaseTender.Options.roles
        _all_forbidden = whitelist()

        _edit_fields = whitelist(
            "procuringEntity",
            "items",
            "value",
            "cause",
            "causeDescription",
            "causeDescription_en",
            "causeDescription_ru",
        )
        _edit_role = _parent_roles["edit"] + _edit_fields
        _read_only_fields = whitelist(
            "lots",
            "contracts",
            # fields below are not covered by the tests
            "awards",
            "cancellations",
        )
        _view_role = _parent_roles["view"] + _edit_fields + _read_only_fields

        roles = {
            "create": _parent_roles["create"] + _edit_fields + whitelist("lots"),
            "edit_draft": _parent_roles["edit_draft"],
            "edit": _edit_role,
            "edit_active": _edit_role,
            "edit_active.awarded": _all_forbidden,
            "edit_complete": _all_forbidden,
            "edit_unsuccessful": _all_forbidden,
            "edit_cancelled": _all_forbidden,
            "view": _view_role,
            "draft": _view_role,
            "active": _view_role,
            "active.awarded": _view_role,
            "complete": _view_role,
            "unsuccessful": _view_role,
            "cancelled": _view_role,
            "Administrator": _parent_roles["Administrator"],
            "chronograph": _parent_roles["chronograph"],
            "chronograph_view": _parent_roles["chronograph_view"],
            "plain": _parent_roles["plain"],
            "listing": _parent_roles["listing"],
            "contracting": _parent_roles["contracting"],
            "default": _parent_roles["default"],
        }

    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
    )  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    value = ModelType(Value, required=True)  # The total estimated value of the procurement.
    procurementMethod = StringType(
        choices=["open", "selective", "limited"], default="limited"
    )  # Specify tendering method as per GPA definitions of Open, Selective, Limited (http://www.wto.org/english/docs_e/legal_e/rev-gpr-94_01_e.htm)
    procurementMethodType = StringType(default="reporting")
    procuringEntity = ModelType(
        ProcuringEntity, required=True
    )  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    awards = ListType(ModelType(Award, required=True), default=list())
    contracts = ListType(ModelType(Contract, required=True), default=list())
    status = StringType(choices=["draft", "active", "complete", "cancelled", "unsuccessful"], default="active")
    mode = StringType(choices=["test"])
    cancellations = ListType(ModelType(ReportingCancellation, required=True), default=list())

    create_accreditations = (ACCR_1, ACCR_3, ACCR_5)
    central_accreditations = (ACCR_5,)
    edit_accreditations = (ACCR_2,)

    procuring_entity_kinds = ["general", "special", "defense", "central", "other"]

    block_complaint_status = OpenUATender.block_complaint_status

    __parent__ = None

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == "Administrator":
            role = "Administrator"
        elif request.authenticated_role == "chronograph":
            role = "chronograph"
        elif request.authenticated_role == "contracting":
            role = "contracting"
        else:
            role = "edit_{}".format(request.context.status)
        return role

    def __acl__(self):
        acl = [
            (Allow, "g:brokers", "create_award_complaint"),
            (Allow, "g:brokers", "create_cancellation_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_tender"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_tender_documents"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_cancellation"),
        ]
        return acl

    # Not required milestones
    def validate_milestones(self, data, value):
        pass


Item = BaseItem


class Award(ReportingAward):

    lotID = MD5Type()

    def validate_lotID(self, data, lotID):
        if isinstance(data["__parent__"], Model):
            if not lotID and data["__parent__"].lots:
                raise ValidationError(u"This field is required.")
            if lotID and lotID not in [lot.id for lot in data["__parent__"].lots if lot]:
                raise ValidationError(u"lotID should be one of lots")

    class Options:
        roles = {"create": award_create_role, "edit": award_edit_role}


class Lot(BaseLot):
    class Options:
        roles = {
            "create": whitelist(
                "id", "title", "title_en", "title_ru", "description", "description_en", "description_ru", "value"
            ),
            "edit": whitelist(
                "title", "title_en", "title_ru", "description", "description_en", "description_ru", "value"
            ),
            "embedded": embedded_lot_role,
            "view": default_lot_role,
            "default": default_lot_role,
            "auction_view": default_lot_role,
            "auction_patch": whitelist("id", "auctionUrl"),
            "chronograph": whitelist("id", "auctionPeriod"),
            "chronograph_view": whitelist("id", "auctionPeriod", "numberOfBids", "status"),
            "Administrator": whitelist("auctionPeriod"),
        }

    value = ModelType(Value, required=True)

    @serializable(serialized_name="value", type=ModelType(Value))
    def lot_value(self):
        return Value(
            dict(
                amount=self.value.amount,
                currency=self.__parent__.value.currency,
                valueAddedTaxIncluded=self.__parent__.value.valueAddedTaxIncluded,
            )
        )


class Contract(BaseContract):
    items = ListType(ModelType(Item, required=True))

    class Options:
        roles = {
            "edit": whitelist(),
            "edit_contract": blacklist("id", "documents", "date", "awardID", "suppliers", "contractID"),
        }

    def get_role(self):
        root = self.get_root()
        request = root.request
        role = "edit"
        if request.authenticated_role == "tender_owner":
            role = "edit_contract"
        return role


@implementer(INegotiationTender)
class NegotiationTender(ReportingTender):
    """ Negotiation """

    class Options:
        namespace = "Tender"
        roles = ReportingTender.Options.roles

    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
    )
    awards = ListType(ModelType(Award, required=True), default=list())
    contracts = ListType(ModelType(Contract, required=True), default=list())
    cause = StringType(
        choices=[
            "artContestIP",
            "noCompetition",
            "twiceUnsuccessful",
            "additionalPurchase",
            "additionalConstruction",
            "stateLegalServices",
        ],
        required=True,
    )
    causeDescription = StringType(required=True, min_length=1)
    causeDescription_en = StringType(min_length=1)
    causeDescription_ru = StringType(min_length=1)
    procurementMethodType = StringType(default="negotiation")

    create_accreditations = (ACCR_3, ACCR_5)
    central_accreditations = (ACCR_5,)
    edit_accreditations = (ACCR_4,)

    procuring_entity_kinds = ["general", "special", "defense", "central"]

    lots = ListType(ModelType(Lot, required=True), default=list(), validators=[validate_lots_uniq])

    cancellations = ListType(ModelType(NegotiationCancellation, required=True), default=list())

    # Required milestones
    def validate_milestones(self, data, value):
        required = get_first_revision_date(data, default=get_now()) > MILESTONES_VALIDATION_FROM
        if required and (value is None or len(value) < 1):
            raise ValidationError("Tender should contain at least one milestone")

    def __acl__(self):
        acl = [
            (Allow, "g:brokers", "create_award_complaint"),
            (Allow, "g:brokers", "create_cancellation_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_cancellation"),
        ]

        self._acl_cancellation(acl)
        return acl

    @serializable(serialize_when_none=False)
    def next_check(self):
        checks = []
        extend_next_check_by_complaint_period_ends(self, checks)
        return min(checks).isoformat() if checks else None


@implementer(INegotiationQuickTender)
class NegotiationQuickTender(NegotiationTender):
    """ Negotiation """

    class Options:
        namespace = "Tender"
        roles = NegotiationTender.Options.roles

    cause = StringType(
        choices=[
            "quick",
            "artContestIP",
            "noCompetition",
            "twiceUnsuccessful",
            "additionalPurchase",
            "additionalConstruction",
            "stateLegalServices",
        ],
        required=False,
    )
    procurementMethodType = StringType(default="negotiation.quick")

    create_accreditations = (ACCR_3, ACCR_5)
    central_accreditations = (ACCR_5,)
    edit_accreditations = (ACCR_4,)

    procuring_entity_kinds = ["general", "special", "defense", "central"]

    def validate_cause(self, data, value):
        required = get_first_revision_date(data, default=get_now()) >= QUICK_CAUSE_REQUIRED_FROM
        if required and value is None:
            raise ValidationError(BaseType.MESSAGES["required"])
