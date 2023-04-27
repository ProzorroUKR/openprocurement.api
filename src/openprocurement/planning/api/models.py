# -*- coding: utf-8 -*-
from itertools import chain
from uuid import uuid4
from copy import deepcopy
from openprocurement.api.models import Document as BaseDocument
from openprocurement.api.models import Model, Period, RootModel, ContactPoint
from openprocurement.api.models import Unit, CPVClassification, Classification, Identifier, Guarantee, Address
from openprocurement.api.models import schematics_embedded_role, schematics_default_role, IsoDateTimeType, ListType
from openprocurement.api.utils import (
    get_now,
    get_first_revision_date,
    to_decimal,
    get_root,
)
from openprocurement.api.validation import validate_cpv_group, validate_items_uniq
from openprocurement.api.interfaces import IOPContent
from openprocurement.api.constants import (
    CPV_ITEMS_CLASS_FROM,
    ADDITIONAL_CLASSIFICATIONS_SCHEMES,
    ADDITIONAL_CLASSIFICATIONS_SCHEMES_2017,
    NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM,
    PLAN_BUYERS_REQUIRED_FROM,
    BUDGET_PERIOD_FROM,
    BUDGET_BREAKDOWN_REQUIRED_FROM,
    PLAN_ADDRESS_KIND_REQUIRED_FROM,
    COUNTRIES,
    UA_REGIONS,
    VALIDATE_ADDRESS_FROM,
)
from openprocurement.api.auth import ACCR_1, ACCR_3, ACCR_5
from openprocurement.planning.api.constants import (
    PROCEDURES,
    MULTI_YEAR_BUDGET_PROCEDURES,
    MULTI_YEAR_BUDGET_MAX_YEARS,
    BREAKDOWN_OTHER,
    BREAKDOWN_TITLES,
    CENTRAL_PROCUREMENT_APPROVE_TIME,
    MILESTONE_APPROVAL_TITLE,
    MILESTONE_APPROVAL_DESCRIPTION,
)
from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist, blacklist
from schematics.types import StringType, IntType, FloatType, BaseType, MD5Type, BooleanType
from schematics.types.compound import ModelType, DictType
from schematics.types.serializable import serializable
from zope.interface import implementer

from openprocurement.tender.pricequotation.validation import validate_profile_pattern

PROCURING_ENTITY_KINDS = ("authority", "central", "defense", "general", "other", "social", "special")

class IPlan(IOPContent):
    """ Base plan marker interface """


class Project(Model):
    """A project """

    id = StringType(required=True)
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()


class BudgetPeriod(Period):
    startDate = IsoDateTimeType(required=True)
    endDate = IsoDateTimeType(required=True)

    def validate_endDate(self, data, value):
        plan = data["__parent__"]["__parent__"]
        if not (isinstance(plan, Model) and plan.tender):
            return
        method_type = plan.tender.procurementMethodType
        start_date = data.get("startDate")
        if method_type not in MULTI_YEAR_BUDGET_PROCEDURES and value.year != start_date.year:
            raise ValidationError("Period startDate and endDate must be within one year for {}.".format(method_type))
        if method_type in MULTI_YEAR_BUDGET_PROCEDURES and value.year - start_date.year > MULTI_YEAR_BUDGET_MAX_YEARS:
            raise ValidationError(
                "Period startDate and endDate must be within {} budget years for {}.".format(
                    MULTI_YEAR_BUDGET_MAX_YEARS + 1, method_type
                )
            )


class BudgetBreakdownItem(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True, choices=BREAKDOWN_TITLES)
    description = StringType(max_length=500)
    description_en = StringType(max_length=500)
    description_ru = StringType(max_length=500)
    value = ModelType(Guarantee, required=True)

    def validate_description(self, data, value):
        if data.get("title", None) == BREAKDOWN_OTHER and not value:
            raise ValidationError(BaseType.MESSAGES["required"])


class Budget(Model):
    """A budget model """

    id = StringType(required=True)
    description = StringType(required=True)
    description_en = StringType()
    description_ru = StringType()
    amount = FloatType(required=True)
    currency = StringType(
        required=False, default="UAH", max_length=3, min_length=3
    )  # The currency in 3-letter ISO 4217 format.
    amountNet = FloatType()
    project = ModelType(Project)
    period = ModelType(BudgetPeriod)
    year = IntType(min_value=2000)
    notes = StringType()
    breakdown = ListType(ModelType(BudgetBreakdownItem, required=True), validators=[validate_items_uniq])

    def validate_period(self, data, value):
        if value:
            if get_now() < BUDGET_PERIOD_FROM:
                raise ValidationError("Can't use period field, use year field instead")
            data["year"] = None

    def validate_year(self, data, value):
        if value and get_now() >= BUDGET_PERIOD_FROM:
            raise ValidationError("Can't use year field, use period field instead")

    def validate_breakdown(self, data, values):
        plan = data["__parent__"]
        if not values:
            validation_date = get_first_revision_date(data, default=get_now())
            if validation_date >= BUDGET_BREAKDOWN_REQUIRED_FROM:
                method = plan.tender.procurementMethodType
                if method not in ("belowThreshold", "reporting", "esco", ""):
                    raise ValidationError(BaseType.MESSAGES["required"])
        else:
            currencies = [i.value.currency for i in values]
            if "currency" in data:
                currencies.append(data["currency"])
            if len(set(currencies)) > 1:
                raise ValidationError("Currency should be identical for all budget breakdown values and budget")
            if isinstance(plan, Model) and plan.tender.procurementMethodType != "esco":
                amounts = [to_decimal(i.value.amount) for i in values]
                if sum(amounts) > to_decimal(data["amount"]):
                    raise ValidationError("Sum of the breakdown values amounts can't be greater than budget amount")


class PlanItem(Model):
    """Simple item model for planing"""

    id = StringType(required=True, min_length=1, default=lambda: uuid4().hex)
    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(Classification, required=True), default=list())
    unit = ModelType(Unit)  # Description of the unit which the good comes in e.g. hours, kilograms
    quantity = FloatType(min_value=0)  # The number of units required
    deliveryAddress = ModelType(Address)
    deliveryDate = ModelType(Period)
    description = StringType(required=True)  # A description of the goods, services to be provided.
    description_en = StringType()
    description_ru = StringType()
    profile = StringType()

    def validate_profile(self, data, value):
        if value:
            validate_profile_pattern(value)

    def validate_classification(self, data, classification):
        plan = data["__parent__"]
        if not plan.classification:
            return
        plan_from_2017 = get_first_revision_date(data, default=get_now()) > CPV_ITEMS_CLASS_FROM
        cpv_336_group = plan.classification.id[:3] == "336"
        base_cpv_code = (
            plan.classification.id[:4] if not cpv_336_group and plan_from_2017 else plan.classification.id[:3]
        )
        if not cpv_336_group and plan_from_2017 and (base_cpv_code != classification.id[:4]):
            raise ValidationError("CPV class of items should be identical to root cpv")
        elif (cpv_336_group or not plan_from_2017) and (base_cpv_code != classification.id[:3]):
            raise ValidationError("CPV group of items be identical to root cpv")

    def validate_additionalClassifications(self, data, items):
        plan = data["__parent__"]
        if not plan.classification:
            return
        plan_date = get_first_revision_date(data, default=get_now())
        plan_from_2017 = plan_date > CPV_ITEMS_CLASS_FROM
        not_cpv = data["classification"]["id"] == "99999999-9"
        if not items and (
            not plan_from_2017 or plan_from_2017 and not_cpv and plan_date < NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM
        ):
            raise ValidationError("This field is required.")
        elif (
            plan_from_2017
            and not_cpv
            and items
            and not any([i.scheme in ADDITIONAL_CLASSIFICATIONS_SCHEMES_2017 for i in items])
        ):
            raise ValidationError(
                "One of additional classifications should be one of [{0}].".format(
                    ", ".join(ADDITIONAL_CLASSIFICATIONS_SCHEMES_2017)
                )
            )
        elif not plan_from_2017 and items and not any([i.scheme in ADDITIONAL_CLASSIFICATIONS_SCHEMES for i in items]):
            raise ValidationError(
                "One of additional classifications should be one of [{0}].".format(
                    ", ".join(ADDITIONAL_CLASSIFICATIONS_SCHEMES)
                )
            )


class BaseOrganization(Model):
    """Base organization"""

    id = MD5Type(default=lambda: uuid4().hex)
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    address = ModelType(Address)
    kind = StringType(choices=PROCURING_ENTITY_KINDS)


class PlanOrganization(BaseOrganization):
    """An organization"""

    def validate_address(self, data, value):
        _parent = data['__parent__']
        validation_date = get_first_revision_date(_parent, default=get_now())
        if validation_date >= PLAN_ADDRESS_KIND_REQUIRED_FROM and not value:
            raise ValidationError(BaseType.MESSAGES["required"])

    def validate_kind(self, data, value):
        _parent = data['__parent__']
        validation_date = get_first_revision_date(_parent, default=get_now())
        if validation_date >= PLAN_ADDRESS_KIND_REQUIRED_FROM and not value:
            raise ValidationError(BaseType.MESSAGES["required"])


class BuyersOrganization(PlanOrganization):
    contactPoint = ModelType(ContactPoint)


class PlanTender(Model):
    """Tender for planning model """

    procurementMethod = StringType(choices=list(PROCEDURES.keys()), default="")
    procurementMethodType = StringType(choices=list(chain(*PROCEDURES.values())), default="")
    tenderPeriod = ModelType(Period, required=True)

    def validate_procurementMethodType(self, data, procurementMethodType):
        _procedures = deepcopy(PROCEDURES)
        _parent = data['__parent__']
        validation_date = get_first_revision_date(_parent, default=get_now())
        if validation_date >= PLAN_ADDRESS_KIND_REQUIRED_FROM:
            _procedures[""] = ("centralizedProcurement", )

        if procurementMethodType not in _procedures[data.get("procurementMethod")]:
            raise ValidationError("Value must be one of {!r}.".format(_procedures[data.get("procurementMethod")]))


class Document(BaseDocument):
    documentOf = StringType(required=False)


class Cancellation(Model):
    class Options:
        _edit_role = whitelist("reason", "reason_en", "status")
        roles = {
            "create": _edit_role,
            "edit": _edit_role,
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    date = IsoDateTimeType(default=get_now)
    reason = StringType(required=True, min_length=1)
    reason_en = StringType()
    status = StringType(choices=["pending", "active"], default="pending")


class Milestone(Model):
    TYPE_APPROVAL = 'approval'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_MET = 'met'
    STATUS_NOT_MET = 'notMet'
    STATUS_INVALID = 'invalid'
    ACTIVE_STATUSES = (STATUS_SCHEDULED, STATUS_MET)

    class Options:
        _edit = whitelist("status", "dueDate", "description")
        _create = _edit + whitelist("title", "description", "type", "author", "documents")
        _view = _create + whitelist("id", "owner", "dateModified", "dateMet")
        roles = {
            "create": _create,
            "edit": _edit,
            "embedded": _view,
            "view": _view,
            "plain": _view + whitelist("owner_token", "transfer_token"),
        }

    def __local_roles__(self):
        return {"{}_{}".format(self.owner, self.owner_token): "milestone_owner"}

    def __acl__(self):
        acl = [
            (Allow, "{}_{}".format(self.owner, self.owner_token), "update_milestone"),
        ]
        return acl

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True, choices=[MILESTONE_APPROVAL_TITLE])
    description = StringType(required=True, min_length=3, default=MILESTONE_APPROVAL_DESCRIPTION)
    type = StringType(required=True, choices=[TYPE_APPROVAL])
    dueDate = IsoDateTimeType(required=True)
    status = StringType(required=True, choices=[STATUS_SCHEDULED, STATUS_MET, STATUS_NOT_MET, STATUS_INVALID],
                        default=STATUS_SCHEDULED)
    documents = ListType(
        ModelType(Document, required=True), default=list()
    )
    author = ModelType(BaseOrganization, required=True)
    dateModified = IsoDateTimeType(default=get_now)
    dateMet = IsoDateTimeType()
    owner = StringType()
    owner_token = StringType()


@implementer(IPlan)
class Plan(RootModel):
    """Plan model"""

    class Options:
        _edit_role = whitelist(
            "procuringEntity", "tender", "budget", "classification", "additionalClassifications", "documents",
            "items", "buyers", "status", "cancellation", "procurementMethodType",
        )
        _create_role = _edit_role + whitelist("mode")
        _common_view = _create_role + whitelist(
            "doc_id", "tender_id", "planID", "datePublished", "owner", "milestones", "switch_status", "dateCreated",
        )
        roles = {
            "plain": _common_view + whitelist("owner_token", "transfer_token"),
            "revision": whitelist("revisions"),
            "create": _create_role,
            "edit": _edit_role,
            "view": _common_view + whitelist("dateModified", "is_masked"),
            "listing": whitelist("dateModified", "doc_id"),  # not used since MongodbResourceListing?
            "Administrator": whitelist("status", "mode", "procuringEntity"),
            "default": schematics_default_role,
        }

    def __local_roles__(self):
        return dict([("{}_{}".format(self.owner, self.owner_token), "plan_owner")])

    # fields

    # procuringEntity:identifier:scheme *
    # procuringEntity:identifier:id *
    # procuringEntity:name *
    # procuringEntity:identifier:legalName *
    procuringEntity = ModelType(PlanOrganization, required=True)

    # tender:tenderPeriod:startDate *
    # tender:procurementMethod *
    tender = ModelType(PlanTender, required=True)

    # budget:project:name
    # budget:project:id
    # budget:id *
    # budget:description *
    # budget:currency
    # budget:amount *
    # budget:amountNet
    budget = ModelType(Budget, required=False)

    # classification:scheme *
    # classification:id *
    # classification:description *
    classification = ModelType(CPVClassification, required=True)

    # additionalClassifications[0]:scheme
    # additionalClassifications[0]:id
    # additionalClassifications[0]:description
    additionalClassifications = ListType(ModelType(Classification, required=True), default=list(), required=False)

    documents = ListType(
        ModelType(Document, required=True), default=list()
    )  # All documents and attachments related to the tender.
    tender_id = MD5Type()
    planID = StringType()
    mode = StringType(choices=["test"])  # flag for test data ?
    items = ListType(ModelType(PlanItem, required=True), required=False, validators=[validate_items_uniq])
    buyers = ListType(ModelType(BuyersOrganization, required=True), min_size=1, max_size=1)
    status = StringType(choices=["draft", "scheduled", "cancelled", "complete"], default="scheduled")
    cancellation = ModelType(Cancellation)
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq], default=list())

    _attachments = DictType(DictType(BaseType), default=dict())  # couchdb attachments
    dateCreated = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    datePublished = IsoDateTimeType(default=get_now)
    owner_token = StringType()
    transfer_token = StringType()
    owner = StringType()
    procurementMethodType = StringType()
    revisions = BaseType(default=list)
    is_masked = BooleanType()

    create_accreditations = (ACCR_1, ACCR_3, ACCR_5)

    __name__ = ""

    def __acl__(self):
        acl = [
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_plan"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_plan_documents"),
        ]
        return acl

    def __repr__(self):
        return "<%s:%r@%r>" % (type(self).__name__, self.id, self.rev)

    @serializable(serialized_name="status")
    def switch_status(self):
        if isinstance(self.cancellation, Cancellation) and self.cancellation.status == "active":
            return "cancelled"
        if self.tender_id is not None:
            return "complete"
        return self.status

    def validate_status(self, data, status):
        if status == "cancelled":
            cancellation = data.get("cancellation")
            if not isinstance(cancellation, Cancellation) or cancellation.status != "active":
                raise ValidationError("An active cancellation object is required")
        elif status == "complete":
            if not data.get("tender_id"):
                method = data.get("tender").get("procurementMethodType")
                if method not in ("belowThreshold", "reporting", ""):
                    raise ValidationError("Can't complete plan with '{}' tender.procurementMethodType".format(method))

    def validate_items(self, data, items):
        cpv_336_group = items[0].classification.id[:3] == "336" if items else False
        if (
            not cpv_336_group
            and get_first_revision_date(data, default=get_now()) > CPV_ITEMS_CLASS_FROM
            and items
            and len(set([i.classification.id[:4] for i in items])) != 1
        ):
            raise ValidationError("CPV class of items should be identical")
        else:
            validate_cpv_group(items)

    def validate_budget(self, data, budget):
        if not budget and data["tender"]["procurementMethodType"] != "esco":
            raise ValidationError("This field is required.")

    def validate_buyers(self, data, value):
        validation_date = get_first_revision_date(data, default=get_now())
        if validation_date >= PLAN_BUYERS_REQUIRED_FROM and not value:
            raise ValidationError(BaseType.MESSAGES["required"])

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.
        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [
            k
            for k in data.keys()
            if data[k] == self.__class__.fields[k].default
            and k not in ("status",)  # save status even if it's changed to default
            or data[k] == getattr(self, k)
        ]
        for k in del_keys:
            del data[k]
        self._data.update(data)
        return self
