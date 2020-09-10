# -*- coding: utf-8 -*-
from uuid import uuid4
from datetime import timedelta, time, datetime
from openprocurement.api.models import OpenprocurementSchematicsDocument, BusinessOrganization, Guarantee
from zope.interface import implementer
from pyramid.security import Allow
from schematics.transforms import whitelist, blacklist, export_loop
from schematics.exceptions import ValidationError
from schematics.types.compound import ModelType, DictType
from schematics.types.serializable import serializable
from schematics.types import StringType, FloatType, URLType, BooleanType, BaseType, MD5Type, IntType
from urlparse import urlparse, parse_qs
from string import hexdigits
from openprocurement.api.interfaces import IOPContent
from openprocurement.api.auth import extract_access_token
from openprocurement.api.models import (
    Revision,
    Organization,
    Identifier,
    Model,
    Period,
    IsoDateTimeType,
    ListType,
    Document as BaseDocument,
    Classification as BaseClassification,
    CPVClassification,
    Location,
    Contract as BaseContract,
    Value,
    PeriodEndRequired as BasePeriodEndRequired,
)
from openprocurement.api.models import Item as BaseItem, Reference
from openprocurement.api.models import schematics_default_role, schematics_embedded_role
from openprocurement.api.validation import validate_items_uniq
from openprocurement.api.utils import (
    generate_docservice_url,
    get_now,
    get_first_revision_date,
    get_root,
    get_uah_amount_from_value,
)
from openprocurement.api.constants import (
    SANDBOX_MODE,
    ADDITIONAL_CLASSIFICATIONS_SCHEMES,
    ADDITIONAL_CLASSIFICATIONS_SCHEMES_2017,
    FUNDERS,
    NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM,
    MPC_REQUIRED_FROM,
    MILESTONES_VALIDATION_FROM,
    RELEASE_2020_04_19,
    COMPLAINT_IDENTIFIER_REQUIRED_FROM,
    CPV_ITEMS_CLASS_FROM,
)
from openprocurement.api.auth import ACCR_1, ACCR_2, ACCR_5

from openprocurement.tender.core.constants import (
    CANT_DELETE_PERIOD_START_DATE_FROM,
    BID_LOTVALUES_VALIDATION_FROM,
    COMPLAINT_AMOUNT_RATE,
    COMPLAINT_MIN_AMOUNT,
    COMPLAINT_MAX_AMOUNT,
    COMPLAINT_ENHANCED_AMOUNT_RATE,
    COMPLAINT_ENHANCED_MIN_AMOUNT,
    COMPLAINT_ENHANCED_MAX_AMOUNT,
)
from openprocurement.tender.core.utils import (
    normalize_should_start_after,
    calc_auction_end_time,
    restrict_value_to_bounds,
    round_up_to_ten,
    get_contract_supplier_roles,
    get_contract_supplier_permissions,
    calculate_tender_date,
    prepare_award_milestones,
    check_skip_award_complaint_period,
    calculate_complaint_business_date,
)
from openprocurement.tender.core.validation import (
    validate_lotvalue_value,
    is_positive_float,
    validate_ua_road,
    validate_gmdn,
    validate_milestones,
    validate_bid_value,
    validate_relatedlot,
    validate_value_type,
    validate_requirement_values,
    validate_minimalstep_limits,
)
from openprocurement.tender.esco.utils import get_complaint_amount as get_esco_complaint_amount
from openprocurement.planning.api.models import BaseOrganization
from logging import getLogger


LOGGER = getLogger(__name__)


view_bid_role = blacklist("owner_token", "owner", "transfer_token") + schematics_default_role
Administrator_bid_role = whitelist("tenderers")

default_lot_role = blacklist("numberOfBids") + schematics_default_role
embedded_lot_role = blacklist("numberOfBids") + schematics_embedded_role


class EnquiryPeriod(Period):
    clarificationsUntil = IsoDateTimeType()
    invalidationDate = IsoDateTimeType()


class PeriodEndRequired(BasePeriodEndRequired):
    def validate_startDate(self, data, period):
        if period and data.get("endDate") and data.get("endDate") < period:
            raise ValidationError(u"period should begin before its end")
        tender = get_tender(data["__parent__"])
        if tender.get("revisions") and tender["revisions"][0].date > CANT_DELETE_PERIOD_START_DATE_FROM and not period:
            raise ValidationError([u"This field cannot be deleted"])


class PeriodStartEndRequired(Period):
    startDate = IsoDateTimeType(required=True, default=get_now)  # The state date for the period.
    endDate = IsoDateTimeType(required=True, default=get_now)  # The end date for the period.


class ITender(IOPContent):
    """ Base tender marker interface """


def get_tender(model):
    while not ITender.providedBy(model):
        model = model.__parent__
    return model


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
            start_after = tender.tenderPeriod.endDate
        return normalize_should_start_after(start_after, tender).isoformat()


class ComplaintModelType(ModelType):
    view_claim_statuses = ["active.enquiries", "active.tendering", "active.auction"]

    def export_loop(self, model_instance, field_converter, role=None, print_none=False):
        """
        Calls the main `export_loop` implementation because they are both
        supposed to operate on models.
        """
        if isinstance(model_instance, self.model_class):
            model_class = model_instance.__class__
        else:
            model_class = self.model_class

        if role in self.view_claim_statuses and getattr(model_instance, "type") == "claim":
            role = "view_claim"

        shaped = export_loop(model_class, model_instance, field_converter, role=role, print_none=print_none)

        if shaped and len(shaped) == 0 and self.allow_none():
            return shaped
        elif shaped:
            return shaped
        elif print_none:
            return shaped


class Document(BaseDocument):
    documentOf = StringType(required=True, choices=["tender", "item", "lot"], default="tender")

    def validate_relatedItem(self, data, relatedItem):
        if not relatedItem and data.get("documentOf") in ["item", "lot"]:
            raise ValidationError(u"This field is required.")
        parent = data["__parent__"]
        if relatedItem and isinstance(parent, Model):
            tender = get_tender(parent)
            if data.get("documentOf") == "lot" and relatedItem not in [i.id for i in tender.lots if i]:
                raise ValidationError(u"relatedItem should be one of lots")
            if data.get("documentOf") == "item" and relatedItem not in [i.id for i in tender.items if i]:
                raise ValidationError(u"relatedItem should be one of items")


class ConfidentialDocumentModelType(ModelType):
    def export_loop(self, model_instance, field_converter, role=None, print_none=False):
        if isinstance(model_instance, self.model_class):
            model_class = model_instance.__class__
        else:
            model_class = self.model_class

        if role not in ["create", "edit", "plain", None] and hasattr(model_instance, "view_role"):
            role = model_instance.view_role()

        shaped = export_loop(model_class, model_instance, field_converter, role=role, print_none=print_none)

        if shaped and len(shaped) == 0 and self.allow_none():
            return shaped
        elif shaped:
            return shaped
        elif print_none:
            return shaped


class ConfidentialDocument(Document):

    class Options:
        namespace = "Document"
        roles = Document.Options.roles
        roles["restricted_view"] = blacklist("url", "download_url") + schematics_default_role

    confidentiality = StringType(choices=["public", "buyerOnly"])
    confidentialityRationale = StringType()

    def view_role(self):
        root = self.get_root()
        request = root.request

        parent = self.__parent__
        tender = parent.__parent__

        acc_token = extract_access_token(request)
        auth_user_id = request.authenticated_userid

        is_owner = (auth_user_id == parent.owner and acc_token == parent.owner_token)
        is_tender_owner = (auth_user_id == tender.owner and acc_token == tender.owner_token)
        access_roles = ["aboveThresholdReviewers", "sas"]

        if (
            not is_owner
            and not is_tender_owner
            and request.authenticated_role not in access_roles
            and self.confidentiality == "buyerOnly"
        ):
            return "restricted_view"

        return "view"

    def validate_confidentialityRationale(self, data, val):
        confidentiality = data.get("confidentiality")
        if confidentiality == "buyerOnly":
            if not val:
                raise ValidationError(u"confidentialityRationale is required")
            elif len(val) < 30:
                raise ValidationError(u"confidentialityRationale should contain at least 30 characters")

    @serializable(serialized_name="url")
    def download_url(self):
        url = self.url
        if self.confidentiality == "buyerOnly":
            return self.url
        if not url or "?download=" not in url:
            return url
        doc_id = parse_qs(urlparse(url).query)["download"][-1]
        root = self.__parent__
        parents = []
        while root.__parent__ is not None:
            parents[0:0] = [root]
            root = root.__parent__
        request = root.request
        if not request.registry.docservice_url:
            return url
        if "status" in parents[0] and parents[0].status in type(parents[0])._options.roles:
            role = parents[0].status
            for index, obj in enumerate(parents):
                if obj.id != url.split("/")[(index - len(parents)) * 2 - 1]:
                    break
                field = url.split("/")[(index - len(parents)) * 2]
                if "_" in field:
                    field = field[0] + field.title().replace("_", "")[1:]
                roles = type(obj)._options.roles
                if roles[role if role in roles else "default"](field, []):
                    return url

        if not self.hash:
            path = [i for i in urlparse(url).path.split("/") if len(i) == 32 and not set(i).difference(hexdigits)]
            return generate_docservice_url(request, doc_id, False, "{}/{}".format(path[0], path[-1]))
        return generate_docservice_url(request, doc_id, False)


class EUConfidentialDocument(ConfidentialDocument):
    confidentiality = StringType(choices=["public", "buyerOnly"], default="public")
    language = StringType(required=True, choices=["uk", "en", "ru"], default="uk")


class EUDocument(Document):
    language = StringType(required=True, choices=["uk", "en", "ru"], default="uk")


def bids_validation_wrapper(validation_func):
    def validator(klass, data, value):
        orig_data = data
        while not isinstance(data["__parent__"], Tender):
            # in case this validation wrapper is used for subelement of bid (such as parameters)
            # traverse back to the bid to get possibility to check status  # troo-to-to =)
            data = data["__parent__"]
        if data["status"] in ("deleted", "invalid", "invalid.pre-qualification", "draft", "unsuccessful"):
            # skip not valid bids
            return
        tender = data["__parent__"]
        request = tender.__parent__.request
        if request.method == "PATCH" and isinstance(tender, Tender) and request.authenticated_role == "tender_owner":
            # disable bids validation on tender PATCH requests as tender bids will be invalidated
            return
        return validation_func(klass, orig_data, value)

    return validator


def bids_response_validation_wrapper(validation_func):
    def validator(klass, data, value):
        orig_data = data
        while not isinstance(data["__parent__"], Tender):
            # in case this validation wrapper is used for subelement of bid (such as response)
            # traverse back to the bid to get possibility to check status  # troo-to-to =)
            data = data["__parent__"]

        tender = data["__parent__"]
        request = tender.__parent__.request

        # TODO: find better solution for check if object created
        if (
            not isinstance(data, (Bid, dict))
            or (request.method == "POST" and request.authenticated_role == "bid_owner" and data["status"] == "draft")
        ):
            return validation_func(klass, orig_data, value)

        if data["status"] in ("deleted", "invalid", "invalid.pre-qualification", "unsuccessful", "draft"):
            # skip not valid bids
            return
        if request.method == "PATCH" and isinstance(tender, Tender) and request.authenticated_role == "tender_owner":
            # disable bids validation on tender PATCH requests as tender bids will be invalidated
            return
        return validation_func(klass, orig_data, value)

    return validator


def validate_dkpp(items, *args):
    if items and not any([i.scheme in ADDITIONAL_CLASSIFICATIONS_SCHEMES for i in items]):
        raise ValidationError(
            u"One of additional classifications should be one of [{0}].".format(
                ", ".join(ADDITIONAL_CLASSIFICATIONS_SCHEMES)
            )
        )


def validate_parameters_uniq(parameters, *args):
    if parameters:
        codes = [i.code for i in parameters]
        if [i for i in set(codes) if codes.count(i) > 1]:
            raise ValidationError(u"Parameter code should be uniq for all parameters")


def validate_values_uniq(values, *args):
    codes = [i.value for i in values]
    if any([codes.count(i) > 1 for i in set(codes)]):
        raise ValidationError(u"Feature value should be uniq for feature")


def validate_features_uniq(features, *args):
    if features:
        codes = [i.code for i in features]
        if any([codes.count(i) > 1 for i in set(codes)]):
            raise ValidationError(u"Feature code should be uniq for all features")


def validate_lots_uniq(lots, *args):
    if lots:
        ids = [i.id for i in lots]
        if [i for i in set(ids) if ids.count(i) > 1]:
            raise ValidationError(u"Lot id should be uniq for all lots")


def validate_funders_unique(funders, *args):
    if funders:
        ids = [(i.identifier.scheme, i.identifier.id) for i in funders]
        if len(funders) > len(set(ids)):
            raise ValidationError(u"Funders' identifier should be unique")


def validate_funders_ids(funders, *args):
    for funder in funders:
        if (funder.identifier.scheme, funder.identifier.id) not in FUNDERS:
            raise ValidationError(u"Funder identifier should be one of the values allowed")


class LotAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        tender = get_tender(self)
        lot = self.__parent__
        statuses = ["active.tendering", "active.auction"]
        if tender.status not in statuses or lot.status != "active":
            return
        if self.startDate and get_now() > calc_auction_end_time(lot.numberOfBids, self.startDate):
            start_after = calc_auction_end_time(lot.numberOfBids, self.startDate)
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


class Item(BaseItem):
    """A good, service, or work to be contracted."""

    classification = ModelType(CPVClassification, required=True)
    deliveryLocation = ModelType(Location)

    def validate_additionalClassifications(self, data, items):
        tender = get_tender(data["__parent__"])
        tender_date = tender.get("revisions")[0].date if tender.get("revisions") else get_now()
        tender_from_2017 = tender_date > CPV_ITEMS_CLASS_FROM
        classification_id = data["classification"]["id"]
        not_cpv = classification_id == "99999999-9"
        required = tender_date < NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM and not_cpv
        if not items and (not tender_from_2017 or tender_from_2017 and not_cpv and required):
            raise ValidationError(u"This field is required.")
        elif (
            tender_from_2017
            and not_cpv
            and items
            and not any([i.scheme in ADDITIONAL_CLASSIFICATIONS_SCHEMES_2017 for i in items])
        ):
            raise ValidationError(
                u"One of additional classifications should be one of [{0}].".format(
                    ", ".join(ADDITIONAL_CLASSIFICATIONS_SCHEMES_2017)
                )
            )
        elif (
            not tender_from_2017 and items and not any([i.scheme in ADDITIONAL_CLASSIFICATIONS_SCHEMES for i in items])
        ):
            raise ValidationError(
                u"One of additional classifications should be one of [{0}].".format(
                    ", ".join(ADDITIONAL_CLASSIFICATIONS_SCHEMES)
                )
            )
        validate_ua_road(classification_id, items)
        validate_gmdn(classification_id, items)

    def validate_relatedLot(self, data, relatedLot):
        parent = data["__parent__"]
        if relatedLot and isinstance(parent, Model):
            validate_relatedlot(get_tender(parent), relatedLot)


class ContractValue(Value):
    amountNet = FloatType(min_value=0)


class Contract(BaseContract):
    class Options:
        roles = {
            "create": blacklist("id", "status", "date", "documents", "dateSigned"),
            "admins": blacklist("id", "documents", "date", "awardID", "suppliers", "items", "contractID"),
            "edit_tender_owner": blacklist("id", "documents", "date", "awardID", "suppliers", "items", "contractID"),
            "edit_contract_supplier": whitelist("status"),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }

    value = ModelType(ContractValue)
    awardID = StringType(required=True)
    documents = ListType(ModelType(Document, required=True), default=list())

    def __acl__(self):
        return get_contract_supplier_permissions(self)

    def get_role(self):
        root = self.get_root()
        request = root.request
        if request.authenticated_role in ("tender_owner", "contract_supplier"):
            role = "edit_{}".format(request.authenticated_role)
        else:
            role = request.authenticated_role
        return role

    def __local_roles__(self):
        roles = {}
        roles.update(get_contract_supplier_roles(self))
        return roles

    def validate_awardID(self, data, awardID):
        parent = data["__parent__"]
        if awardID and isinstance(parent, Model) and awardID not in [i.id for i in parent.awards]:
            raise ValidationError(u"awardID should be one of awards")

    def validate_dateSigned(self, data, value):
        parent = data["__parent__"]
        if value and isinstance(parent, Model):
            tender = get_tender(parent)
            skip_award_complaint_period = check_skip_award_complaint_period(tender)
            award = [i for i in parent.awards if i.id == data["awardID"]][0]
            if award.complaintPeriod:
                if not skip_award_complaint_period:
                    if award.complaintPeriod.endDate and value <= award.complaintPeriod.endDate:
                        raise ValidationError(
                            u"Contract signature date should be after award complaint period end date ({})".format(
                                award.complaintPeriod.endDate.isoformat()
                            )
                        )
                elif award.complaintPeriod.startDate and value <= award.complaintPeriod.startDate:
                        raise ValidationError(
                            u"Contract signature date should be after award activation date ({})".format(
                                award.complaintPeriod.startDate.isoformat()
                            )
                        )

            if value > get_now():
                raise ValidationError(u"Contract signature date can't be in the future")


class LotValue(Model):
    class Options:
        roles = {
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
            "create": whitelist("value", "relatedLot"),
            "edit": whitelist("value", "relatedLot"),
            "auction_view": whitelist("value", "date", "relatedLot", "participationUrl"),
            "auction_post": whitelist("value", "date", "relatedLot"),
            "auction_patch": whitelist("participationUrl", "relatedLot"),
        }

    value = ModelType(Value, required=True)
    relatedLot = MD5Type(required=True)
    participationUrl = URLType()
    date = IsoDateTimeType(default=get_now)

    def validate_value(self, data, value):
        parent = data["__parent__"]
        if isinstance(parent, Model):
            validate_lotvalue_value(get_tender(parent), data["relatedLot"], value)

    def validate_relatedLot(self, data, relatedLot):
        parent = data["__parent__"]
        if isinstance(parent, Model):
            validate_relatedlot(get_tender(parent), relatedLot)


class Parameter(Model):
    code = StringType(required=True)
    value = FloatType(required=True)

    def validate_code(self, data, code):
        parent = data["__parent__"]
        if isinstance(parent, Model) and code not in [i.code for i in (get_tender(parent).features or [])]:
            raise ValidationError(u"code should be one of feature code.")

    def validate_value(self, data, value):
        parent = data["__parent__"]
        if isinstance(parent, Model):
            tender = get_tender(parent)
            codes = dict([(i.code, [x.value for x in i.enum]) for i in (tender.features or [])])
            if data["code"] in codes and value not in codes[data["code"]]:
                raise ValidationError(u"value should be one of feature value.")


class FeatureValue(Model):
    value = FloatType(required=True, min_value=0.0, max_value=0.3)
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()


class Feature(Model):
    code = StringType(required=True, min_length=1, default=lambda: uuid4().hex)
    featureOf = StringType(required=True, choices=["tenderer", "lot", "item"], default="tenderer")
    relatedItem = StringType(min_length=1)
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    enum = ListType(
        ModelType(FeatureValue, required=True), default=list(), min_size=1, validators=[validate_values_uniq]
    )

    def validate_relatedItem(self, data, relatedItem):
        if not relatedItem and data.get("featureOf") in ["item", "lot"]:
            raise ValidationError(u"This field is required.")
        parent = data["__parent__"]
        if isinstance(parent, Model):
            if data.get("featureOf") == "item" and relatedItem not in [i.id for i in parent.items if i]:
                raise ValidationError(u"relatedItem should be one of items")
            if data.get("featureOf") == "lot" and relatedItem not in [i.id for i in parent.lots if i]:
                raise ValidationError(u"relatedItem should be one of lots")


# ECriteria
class EligibleEvidence(Model):
    class Options:
        namespace = "Evidence"
        roles = {
            "create": blacklist(),
            "edit": blacklist("type"),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }

    id = StringType(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    type = StringType(
        choices=["document", "statement"],
        default="statement"
    )


class Evidence(EligibleEvidence):
    class Options:
        namespace = "Evidence"
        roles = {
            "create": blacklist(),
            "edit": blacklist(),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }
    relatedDocument = ModelType(Reference)

    @bids_response_validation_wrapper
    def validate_relatedDocument(self, data, document_reference):
        if data["type"] in ["document"] and not document_reference:
            raise ValidationError("This field is required.")

        if document_reference:
            requirement_response = data["__parent__"]
            parent = requirement_response["__parent__"]
            parent_name = parent.__class__.__name__.lower()
            if document_reference.id not in [document.id for document in parent.documents if document]:
                raise ValidationError("relatedDocument.id should be one of {} documents".format(parent_name))

    @bids_response_validation_wrapper
    def validate_type(self, data, value):
        parent = data["__parent__"]
        requirement_reference = parent.requirement
        if value and requirement_reference and isinstance(parent, Model):
            tender = get_tender(parent)
            requirement = None
            for criteria in tender.criteria:
                for group in criteria.requirementGroups:
                    for req in group.requirements:
                        if req.id == requirement_reference.id:
                            requirement = req
                            break
            if requirement:
                evidences_type = [i.type for i in requirement.eligibleEvidences]
                if evidences_type and value not in evidences_type:
                    raise ValidationError("type should be one of eligibleEvidences types")


class ExtendPeriod(Period):
    maxExtendDate = IsoDateTimeType()
    durationInDays = IntType()
    duration = StringType()


class LegislationIdentifier(Identifier):
    scheme = StringType()


class LegislationItem(Model):
    version = StringType()
    identifier = ModelType(LegislationIdentifier, required=True)
    type = StringType(choices=["NATIONAL_LEGISLATION"], default="NATIONAL_LEGISLATION")
    article = StringType()


class Requirement(Model):
    class Options:
        roles = {
            "create": blacklist("eligibleEvidences"),
            "edit": blacklist("eligibleEvidences"),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }

    id = StringType(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    dataType = StringType(required=True,
                          choices=["string", "number", "integer", "boolean", "date-time"])

    minValue = StringType()
    maxValue = StringType()
    period = ModelType(ExtendPeriod)
    eligibleEvidences = ListType(ModelType(EligibleEvidence, required=True), default=list())
    relatedFeature = MD5Type()
    expectedValue = StringType()

    def validate_minValue(self, data, value):
        if value:
            if data["dataType"] not in ["integer", "number"]:
                raise ValidationError("minValue must be integer or number")
            validate_value_type(value, data['dataType'])

    def validate_maxValue(self, data, value):
        if value:
            if data["dataType"] not in ["integer", "number"]:
                raise ValidationError("minValue must be integer or number")
            validate_value_type(value, data['dataType'])

    def validate_expectedValue(self, data, value):
        if value:
            validate_value_type(value, data['dataType'])

    def validate_relatedFeature(self, data, feature_id):
        parent = data["__parent__"]
        if feature_id and isinstance(parent, Model):
            tender = get_tender(parent)
            features = [] if not tender.get("features") else tender.get("features")
            if feature_id not in [feature.id for feature in features]:
                raise ValidationError("relatedFeature should be one of features")


class RequirementGroup(Model):
    class Options:
        roles = {
            "create": blacklist(),
            "edit": blacklist("requirements"),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    requirements = ListType(
        ModelType(Requirement, required=True, validators=[validate_requirement_values]),
        default=list(),
    )


class CriterionClassification(BaseClassification):
    description = StringType()


class Criterion(Model):
    class Options:
        roles = {
            "create": blacklist(),
            "edit": blacklist(
                "requirementGroups",
                "additionalClassifications",
                "legislation",
            ),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()

    source = StringType(choices=["tenderer", "buyer", "procuringEntity", "ssrBot", "winner"])
    relatesTo = StringType(choices=["tenderer", "item", "lot"])
    relatedItem = MD5Type()
    classification = ModelType(CriterionClassification, required=True) # TODO: make it required
    additionalClassifications = ListType(ModelType(BaseClassification, required=True), default=list())
    legislation = ListType(ModelType(LegislationItem, required=True), default=list())
    requirementGroups = ListType(
        ModelType(RequirementGroup, required=True),
        required=True,
        min_size=1,
    )

    def validate_relatedItem(self, data, relatedItem):
        if not relatedItem and data.get("relatesTo") in ["item", "lot"]:
            raise ValidationError(u"This field is required.")
        parent = data["__parent__"]
        if relatedItem and isinstance(parent, Model):
            tender = get_tender(parent)
            if data.get("relatesTo") == "lot" and relatedItem not in [i.id for i in tender.lots if i]:
                raise ValidationError(u"relatedItem should be one of lots")
            if data.get("relatesTo") == "item" and relatedItem not in [i.id for i in tender.items if i]:
                raise ValidationError(u"relatedItem should be one of items")


class RequirementResponse(Model):
    class Options:
        roles = {
            "create": blacklist("evidences"),
            "edit": blacklist("evidences"),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }
    id = StringType(required=True, default=lambda: uuid4().hex)
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()

    period = ModelType(ExtendPeriod)
    requirement = ModelType(Reference, required=True)
    relatedTenderer = ModelType(Reference)
    relatedItem = MD5Type()
    evidences = ListType(ModelType(Evidence, required=True), default=list())

    value = StringType(required=True)

    @bids_response_validation_wrapper
    def validate_relatedItem(self, data, relatedItem):
        parent = data["__parent__"]
        if relatedItem and isinstance(parent, Model):
            tender = get_tender(parent)
            if relatedItem not in [i.id for i in tender.items if i]:
                raise ValidationError(u"relatedItem should be one of items")

    @bids_response_validation_wrapper
    def validate_relatedTenderer(self, data, relatedTenderer):
        parent = data["__parent__"]
        if relatedTenderer and isinstance(parent, Model):
            if relatedTenderer.id not in [
                organization.identifier.id
                for organization in parent.get("tenderers", list())
            ]:
                raise ValidationError(u"relatedTenderer should be one of bid tenderers")

    @bids_response_validation_wrapper
    def validate_requirement(self, data, requirement):
        parent = data["__parent__"]

        if requirement and requirement.get("id") and isinstance(parent, Model):
            tender = get_tender(parent)
            requirement_id = requirement["id"]

            requirements = [
                requirement.id
                for criteria in tender.criteria
                for group in criteria.requirementGroups
                for requirement in group.requirements
                if requirement.id == requirement_id
            ]

            if not requirements:
                raise ValidationError("requirement should be one of criteria requirements")

    @bids_response_validation_wrapper
    def validate_value(self, data, value):
        requirement_reference = data.get("requirement")
        parent = data["__parent__"]
        if isinstance(parent, Model):
            tender = get_tender(parent)
            requirement = None
            for criteria in tender.criteria:
                for group in criteria.requirementGroups:
                    for req in group.requirements:
                        if req.id == requirement_reference.id:
                            requirement = req
                            break
            if requirement:
                data_type = requirement.dataType
                valid_value = validate_value_type(value, data_type)
                expectedValue = requirement.get("expectedValue")
                minValue = requirement.get("minValue")
                maxValue = requirement.get("maxValue")

                if expectedValue and validate_value_type(expectedValue, data_type) != valid_value:
                    raise ValidationError("value and requirementGroup.expectedValue must be equal")
                if minValue and valid_value < validate_value_type(minValue, data_type):
                    raise ValidationError("value should be higher than eligibleEvidence.minValue")
                if maxValue and valid_value > validate_value_type(maxValue, data_type):
                    raise ValidationError("value should be lower than eligibleEvidence.maxValue")

                return valid_value


class Bid(Model):
    class Options:
        roles = {
            "Administrator": Administrator_bid_role,
            "embedded": view_bid_role,
            "view": view_bid_role,
            "create": whitelist("value", "status", "tenderers", "parameters", "lotValues", "documents"),
            "edit": whitelist("value", "status", "tenderers", "parameters", "lotValues"),
            "auction_view": whitelist("value", "lotValues", "id", "date", "parameters", "participationUrl"),
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
        }

    def __local_roles__(self):
        return dict([("{}_{}".format(self.owner, self.owner_token), "bid_owner")])

    tenderers = ListType(ModelType(BusinessOrganization, required=True), required=True, min_size=1, max_size=1)
    parameters = ListType(ModelType(Parameter, required=True), default=list(), validators=[validate_parameters_uniq])
    lotValues = ListType(ModelType(LotValue, required=True), default=list())
    date = IsoDateTimeType(default=get_now)
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(choices=["active", "draft"], default="active")
    value = ModelType(Value)
    documents = ListType(ModelType(Document, required=True), default=list())
    participationUrl = URLType()
    owner_token = StringType()
    transfer_token = StringType()
    owner = StringType()
    requirementResponses = ListType(
        ModelType(RequirementResponse, required=True),
        default=list()
    )

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
        return [(Allow, "{}_{}".format(self.owner, self.owner_token), "edit_bid")]

    def validate_participationUrl(self, data, url):
        parent = data["__parent__"]
        if url and isinstance(parent, Model) and get_tender(parent).lots:
            raise ValidationError(u"url should be posted for each lot of bid")

    def validate_lotValues(self, data, values):
        parent = data["__parent__"]
        if isinstance(parent, Model):
            tender = parent
            if tender.lots and not values:
                raise ValidationError(u"This field is required.")
            if tender.get("revisions") and tender["revisions"][0].date > BID_LOTVALUES_VALIDATION_FROM and values:
                lots = [i.relatedLot for i in values]
                if len(lots) != len(set(lots)):
                    raise ValidationError(u"bids don't allow duplicated proposals")

    def validate_value(self, data, value):
        parent = data["__parent__"]
        if isinstance(parent, Model):
            validate_bid_value(parent, value)

    def validate_parameters(self, data, parameters):
        parent = data["__parent__"]
        if isinstance(parent, Model):
            tender = parent
            if tender.lots:
                lots = [i.relatedLot for i in data["lotValues"]]
                items = [i.id for i in tender.items if i.relatedLot in lots]
                codes = dict(
                    [
                        (i.code, [x.value for x in i.enum])
                        for i in (tender.features or [])
                        if i.featureOf == "tenderer"
                        or i.featureOf == "lot"
                        and i.relatedItem in lots
                        or i.featureOf == "item"
                        and i.relatedItem in items
                    ]
                )
                if set([i["code"] for i in parameters]) != set(codes):
                    raise ValidationError(u"All features parameters is required.")
            elif not parameters and tender.features:
                raise ValidationError(u"This field is required.")
            elif set([i["code"] for i in parameters]) != set([i.code for i in (tender.features or [])]):
                raise ValidationError(u"All features parameters is required.")


PROCURING_ENTITY_KINDS = ("authority", "central", "defense", "general", "other", "social", "special")


class ProcuringEntity(Organization):
    """An organization."""

    class Options:
        roles = {
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
            "edit_active.enquiries": schematics_default_role + blacklist("kind"),
            "edit_active.tendering": schematics_default_role + blacklist("kind"),
        }

    kind = StringType(choices=PROCURING_ENTITY_KINDS)


class Question(Model):
    class Options:
        roles = {
            "create": whitelist("author", "title", "description", "questionOf", "relatedItem"),
            "edit": whitelist("answer"),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
            "active.enquiries": (blacklist("author") + schematics_embedded_role),
            "active.tendering": (blacklist("author") + schematics_embedded_role),
            "active.auction": (blacklist("author") + schematics_embedded_role),
            "active.pre-qualification": (blacklist("author") + schematics_embedded_role),
            "active.pre-qualification.stand-still": (blacklist("author") + schematics_embedded_role),
            "active.qualification": schematics_default_role,
            "active.awarded": schematics_default_role,
            "complete": schematics_default_role,
            "unsuccessful": schematics_default_role,
            "cancelled": schematics_default_role,
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    author = ModelType(
        Organization, required=True
    )  # who is asking question (contactPoint - person, identification - organization that person represents)
    title = StringType(required=True)  # title of the question
    description = StringType()  # description of the question
    date = IsoDateTimeType(default=get_now)  # autogenerated date of posting
    answer = StringType()  # only tender owner can post answer
    questionOf = StringType(required=True, choices=["tender", "item", "lot"], default="tender")
    relatedItem = StringType(min_length=1)
    dateAnswered = IsoDateTimeType()

    def validate_relatedItem(self, data, relatedItem):
        if not relatedItem and data.get("questionOf") in ["item", "lot"]:
            raise ValidationError(u"This field is required.")
        parent = data["__parent__"]
        if relatedItem and isinstance(parent, Model):
            tender = get_tender(parent)
            if data.get("questionOf") == "lot" and relatedItem not in [i.id for i in tender.lots if i]:
                raise ValidationError(u"relatedItem should be one of lots")
            if data.get("questionOf") == "item" and relatedItem not in [i.id for i in tender.items if i]:
                raise ValidationError(u"relatedItem should be one of items")


class ComplaintIdentifier(Identifier):
    class Options:
        roles = {
            "draft_complaint": whitelist("uri", "legalName_ru", "legalName_en"),
        }

    def validate_id(self, data, identifier_id):
        if not identifier_id:
            complaint = data["__parent__"]["__parent__"]
            if complaint.type == "complaint":
                tender = get_root(data["__parent__"])
                if get_first_revision_date(tender, default=get_now()) > COMPLAINT_IDENTIFIER_REQUIRED_FROM:
                    raise ValidationError(u"This field is required.")

    def validate_legalName(self, data, legalName):
        if not legalName:
            complaint = data["__parent__"]["__parent__"]
            if complaint.type == "complaint":
                tender = get_root(data["__parent__"])
                if get_first_revision_date(tender, default=get_now()) > COMPLAINT_IDENTIFIER_REQUIRED_FROM:
                    raise ValidationError(u"This field is required.")


class ComplaintOrganization(Organization):
    identifier = ModelType(ComplaintIdentifier, required=True)


class ComplaintAuthorModelType(ModelType):
    def export_loop(self, model_instance, field_converter, role=None, print_none=False):
        if role == "draft" and getattr(model_instance.__parent__, "type") == "complaint":
            request = model_instance.get_root().request
            tender = request.validated["tender"]
            if get_first_revision_date(tender, default=get_now()) > COMPLAINT_IDENTIFIER_REQUIRED_FROM:
                role = "draft_complaint"
        return super(ComplaintAuthorModelType, self).export_loop(model_instance, field_converter,
                                                                 role=role, print_none=print_none)


class Complaint(Model):
    class Options:
        roles = {
            "create": whitelist("author", "title", "description", "status", "type", "relatedLot"),
            "draft": whitelist("author", "title", "description", "status"),
            "cancellation": whitelist("cancellationReason", "status"),
            "satisfy": whitelist("satisfied", "status"),
            "answer": whitelist("resolution", "resolutionType", "status", "tendererAction"),
            "action": whitelist("tendererAction"),
            "review": whitelist("decision", "status"),
            "view": view_bid_role,
            "view_claim": (blacklist("author") + view_bid_role),
            "Administrator": whitelist("value"),
        }
        for _tender_status in (
            "active.enquiries",
            "active.tendering",
            "active.auction",
            "active.qualification",
            "active.awarded",
            "complete",
            "unsuccessful",
            "cancelled",
            "active.pre-qualification",  # openeu
            "active.pre-qualification.stand-still",
            "active.qualification.stand-still",  # cfaua
            "active.stage2.pending",  # competitive dialogue
            "active.stage2.waiting",
            "draft.stage2",
            "active",  # limited
        ):  # if there is no role, all the fields including(tokens) will be shown if context is the tender
            roles[_tender_status] = view_bid_role

    # system
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    complaintID = StringType()
    date = IsoDateTimeType(default=get_now)  # autogenerated date of posting
    status = StringType(
        choices=[
            "draft",
            "claim",
            "answered",
            "pending",
            "invalid",
            "resolved",
            "declined",
            "cancelled",
            "ignored",
            "mistaken"
        ],
        default="draft",
    )
    documents = ListType(ModelType(Document, required=True), default=list())
    type = StringType(
        choices=["claim", "complaint"],
    )  # 'complaint' if status in ['pending'] or 'claim' if status in ['draft', 'claim', 'answered']
    owner_token = StringType()
    transfer_token = StringType()
    owner = StringType()
    relatedLot = MD5Type()
    # complainant
    author = ComplaintAuthorModelType(ComplaintOrganization, required=True)  # author of claim
    title = StringType(required=True)  # title of the claim
    description = StringType()  # description of the claim
    dateSubmitted = IsoDateTimeType()
    # tender owner
    resolution = StringType()
    resolutionType = StringType(choices=["invalid", "resolved", "declined"])
    dateAnswered = IsoDateTimeType()
    tendererAction = StringType()
    tendererActionDate = IsoDateTimeType()
    # complainant
    satisfied = BooleanType()
    dateEscalated = IsoDateTimeType()
    # reviewer
    decision = StringType()
    dateDecision = IsoDateTimeType()
    # complainant
    cancellationReason = StringType()
    dateCanceled = IsoDateTimeType()

    value = ModelType(Guarantee)
    rejectReason = StringType(choices=[
        "buyerViolationsCorrected",
        "lawNonCompliance",
        "alreadyExists",
        "tenderCancelled",
        "cancelledByComplainant",
        "complaintPeriodEnded",
        "incorrectPayment"
    ])

    @serializable(serialized_name="value", serialize_when_none=False)
    def calculate_value(self):
        # should be calculated only once for draft complaints
        if not self.value and self.status == "draft" and self.type == "complaint":
            request = self.get_root().request
            tender = request.validated["tender"]
            if get_first_revision_date(tender, default=get_now()) > RELEASE_2020_04_19:
                if tender["procurementMethodType"] == "esco":
                    amount = get_esco_complaint_amount(request, tender, self)
                else:
                    related_lot = self.get_related_lot_obj(tender)
                    value = related_lot["value"] if related_lot else tender["value"]
                    base_amount = get_uah_amount_from_value(
                        request, value, {"complaint_id": self.id}
                    )
                    if tender["status"] == "active.tendering":
                        amount = restrict_value_to_bounds(
                            base_amount * COMPLAINT_AMOUNT_RATE,
                            COMPLAINT_MIN_AMOUNT,
                            COMPLAINT_MAX_AMOUNT
                        )
                    else:
                        amount = restrict_value_to_bounds(
                            base_amount * COMPLAINT_ENHANCED_AMOUNT_RATE,
                            COMPLAINT_ENHANCED_MIN_AMOUNT,
                            COMPLAINT_ENHANCED_MAX_AMOUNT
                        )
                return dict(amount=round_up_to_ten(amount), currency="UAH")

    def serialize(self, role=None, context=None):
        if (
            role == "view"
            and self.type == "claim"
            and get_tender(self).status in ["active.enquiries", "active.tendering"]
        ):
            role = "view_claim"
        return super(Complaint, self).serialize(role=role, context=context)

    def get_role(self):
        root = self.get_root()
        request = root.request
        data = request.json_body["data"]
        auth_role = request.authenticated_role
        status = data.get("status", self.status)
        if auth_role == "Administrator":
            role = auth_role
        elif auth_role == "complaint_owner" and status == "cancelled":
            role = "cancellation"
        elif auth_role == "complaint_owner" and self.status == "draft":
            role = "draft"
        elif auth_role == "tender_owner" and self.status == "claim":
            role = "answer"
        elif auth_role == "complaint_owner" and self.status == "answered":
            role = "satisfy"
        else:
            role = "invalid"
        return role

    def __local_roles__(self):
        return dict([("{}_{}".format(self.owner, self.owner_token), "complaint_owner")])

    def __acl__(self):
        return [
            (Allow, "g:reviewers", "edit_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_complaint_documents"),
        ]

    def validate_type(self, data, value):
        if not value:
            tender = get_root(data["__parent__"])
            if get_first_revision_date(tender, default=get_now()) > RELEASE_2020_04_19:
                raise ValidationError("This field is required")
            else:
                data["type"] = "claim"

    def validate_resolutionType(self, data, resolutionType):
        if not resolutionType and data.get("status") == "answered":
            raise ValidationError(u"This field is required.")

    def validate_cancellationReason(self, data, cancellationReason):
        if not cancellationReason and data.get("status") == "cancelled":
            raise ValidationError(u"This field is required.")

    def validate_relatedLot(self, data, relatedLot):
        parent = data["__parent__"]
        if relatedLot and isinstance(parent, Model):
            validate_relatedlot(get_tender(parent), relatedLot)

    def get_related_lot_obj(self, tender):
        lot_id = (
            self.get("relatedLot")  # tender lot
            or self.get("__parent__").get("lotID")  # award or qualification
            or self.get("__parent__").get("relatedLot")  # cancellation
        )
        if lot_id:
            for lot in tender.get("lots", ""):
                if lot["id"] == lot_id:
                    return lot


class Cancellation(Model):
    class Options:
        roles = {
            "create": whitelist("reason", "status", "reasonType", "cancellationOf", "relatedLot"),
            "edit": whitelist("status", "reasonType"),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }

    @serializable(serialized_name="status")
    def default_status(self):
        if not self.status:
            if get_first_revision_date(self.__parent__, default=get_now()) > RELEASE_2020_04_19:
                return "draft"
            return "pending"
        return self.status

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    reason = StringType(required=True)
    reason_en = StringType()
    reason_ru = StringType()
    date = IsoDateTimeType(default=get_now)
    status = StringType()
    documents = ListType(ModelType(Document, required=True), default=list())
    cancellationOf = StringType(required=True, choices=["tender", "lot"], default="tender")
    relatedLot = MD5Type()

    reasonType = StringType()

    _before_release_reasonType_choices = ["cancelled", "unsuccessful"]
    _after_release_reasonType_choices = ["noDemand", "unFixable", "forceMajeure", "expensesCut"]

    _before_release_status_choices = ["pending", "active"]
    _after_release_status_choices = ["draft", "pending", "unsuccessful", "active"]

    def validate_relatedLot(self, data, relatedLot):
        if not relatedLot and data.get("cancellationOf") == "lot":
            raise ValidationError(u"This field is required.")
        parent = data["__parent__"]
        if relatedLot and isinstance(parent, Model) and relatedLot not in [i.id for i in parent.lots if i]:
            raise ValidationError(u"relatedLot should be one of lots")

    def validate_status(self, data, value):
        tender = get_root(data["__parent__"])
        cancellation_of = data.get('cancellationOf')

        choices = (
            self._after_release_status_choices
            if get_first_revision_date(tender, default=get_now()) > RELEASE_2020_04_19
            else self._before_release_status_choices
        )

        if value and value not in choices:
            raise ValidationError("Value must be one of %s" % choices)

    def validate_reasonType(self, data, value):
        tender = get_root(data["__parent__"])
        if get_first_revision_date(tender, default=get_now()) > RELEASE_2020_04_19:
            choices = self._after_release_reasonType_choices
            if not value:
                raise ValidationError("This field is required")
        else:
            choices = self._before_release_reasonType_choices
            if not choices and value:
                raise ValidationError("Rogue field")

            elif not choices and not value:
                return

            elif not value and choices:
                data["reasonType"] = choices[0]
                return

        if value not in choices:
            raise ValidationError("Value must be one of %s" % choices)


class BaseAward(Model):
    """ Base award """

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType()  # Award title
    title_en = StringType()
    title_ru = StringType()
    subcontractingDetails = StringType()
    qualified = BooleanType()
    description = StringType()  # Award description
    description_en = StringType()
    description_ru = StringType()
    status = StringType(required=True, choices=["pending", "unsuccessful", "active", "cancelled"], default="pending")
    date = IsoDateTimeType(default=get_now)
    value = ModelType(Value)
    suppliers = ListType(ModelType(BusinessOrganization, required=True), required=True, min_size=1, max_size=1)
    documents = ListType(ModelType(Document, required=True), default=list())
    items = ListType(ModelType(Item, required=True))

    requirementResponses = ListType(ModelType(RequirementResponse, required=True), default=list())


class QualificationMilestone(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    CODE_24_HOURS = "24h"
    CODE_LOW_PRICE = "alp"
    code = StringType(required=True, choices=[CODE_24_HOURS, CODE_LOW_PRICE])
    dueDate = IsoDateTimeType()
    description = StringType()
    date = IsoDateTimeType(default=get_now)

    class Options:
        namespace = "Milestone"
        roles = {
            "create": whitelist("code", "description"),
            "Administrator": whitelist("dueDate"),
            "view": schematics_default_role,
        }

    @serializable(serialized_name="dueDate")
    def set_due_date(self):
        if not self.dueDate:
            if self.code == self.CODE_24_HOURS:
                self.dueDate = calculate_tender_date(
                    self.date, timedelta(hours=24), get_tender(self)
                )
            elif self.code == self.CODE_LOW_PRICE:
                self.dueDate = calculate_complaint_business_date(
                    self.date, timedelta(days=1), get_tender(self), working_days=True
                )
        return self.dueDate and self.dueDate.isoformat()


class QualificationMilestoneListMixin(Model):
    milestones = ListType(ModelType(QualificationMilestone, required=True), default=list())

    def validate_milestones(self, data, milestones):
        """
        This validation on the model, not on the view
        because there is a way to post milestone to different zones (couchdb masters)
        and concord will merge them, that shouldn't be the case
        """
        if len(filter(lambda m: m.code == QualificationMilestone.CODE_24_HOURS, milestones)) > 1:
            raise ValidationError(u"There can be only one '24h' milestone")


class Award(BaseAward):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """

    class Options:
        roles = {
            "create": blacklist("id", "status", "date", "documents", "complaints", "complaintPeriod"),
            "edit": whitelist(
                "status", "title", "title_en", "title_ru", "description", "description_en", "description_ru"
            ),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
            "Administrator": whitelist("complaintPeriod"),
        }

    bid_id = MD5Type(required=True)
    lotID = MD5Type()
    complaints = ListType(ModelType(Complaint, required=True), default=list())
    complaintPeriod = ModelType(Period)

    def validate_lotID(self, data, lotID):
        parent = data["__parent__"]
        if isinstance(parent, Model):
            if not lotID and parent.lots:
                raise ValidationError(u"This field is required.")
            if lotID and lotID not in [lot.id for lot in parent.lots if lot]:
                raise ValidationError(u"lotID should be one of lots")


class BaseLot(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    date = IsoDateTimeType()
    status = StringType(choices=["active", "cancelled", "unsuccessful", "complete"], default="active")


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
            "Administrator": whitelist("auctionPeriod"),
        }

    value = ModelType(Value, required=True)
    minimalStep = ModelType(Value, required=True)
    auctionPeriod = ModelType(LotAuctionPeriod, default={})
    auctionUrl = URLType()
    guarantee = ModelType(Guarantee)

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        bids = [
            bid
            for bid in self.__parent__.bids
            if self.id in [i.relatedLot for i in bid.lotValues] and getattr(bid, "status", "active") == "active"
        ]
        return len(bids)

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def lot_guarantee(self):
        if self.guarantee:
            currency = self.__parent__.guarantee.currency if self.__parent__.guarantee else self.guarantee.currency
            return Guarantee(dict(amount=self.guarantee.amount, currency=currency))

    @serializable(serialized_name="minimalStep", type=ModelType(Value))
    def lot_minimalStep(self):
        return Value(
            dict(
                amount=self.minimalStep.amount,
                currency=self.__parent__.minimalStep.currency,
                valueAddedTaxIncluded=self.__parent__.minimalStep.valueAddedTaxIncluded,
            )
        )

    @serializable(serialized_name="value", type=ModelType(Value))
    def lot_value(self):
        return Value(
            dict(
                amount=self.value.amount,
                currency=self.__parent__.value.currency,
                valueAddedTaxIncluded=self.__parent__.value.valueAddedTaxIncluded,
            )
        )

    def validate_minimalStep(self, data, value):
        if value and value.amount and data.get("value"):
            if data.get("value").amount < value.amount:
                raise ValidationError(u"value should be less than value of lot")


class LotWithMinimalStepLimitsValidation(Lot):
    """Additional minimalStep validation for :
        belowThreshold
        aboveThresholdUA
        aboveThresholdEU
        aboveThresholdUA.defense
        competitiveDialogueUA.stage1
        competitiveDialogueEU.stage1
        closeFrameworkAgreementUA
    """
    class Options:
        namespace = "Lot"

    def validate_minimalStep(self, data, value):
        if value and value.amount and data.get("value"):
            if data.get("value").amount < value.amount:
                raise ValidationError(u"value should be less than value of lot")
        validate_minimalstep_limits(data, value)


class Duration(Model):
    days = IntType(required=True, min_value=1)
    type = StringType(required=True, choices=["working", "banking", "calendar"])

    def validate_days(self, data, value):
        tender = get_root(data["__parent__"])
        if get_first_revision_date(tender, default=get_now()) > MILESTONES_VALIDATION_FROM and value > 1000:
            raise ValidationError(u"days shouldn't be more than 1000")


class Milestone(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(
        required=True,
        choices=[
            "executionOfWorks",
            "deliveryOfGoods",
            "submittingServices",
            "signingTheContract",
            "submissionDateOfApplications",
            "dateOfInvoicing",
            "endDateOfTheReportingPeriod",
            "anotherEvent",
        ],
    )
    description = StringType()
    type = StringType(required=True, choices=["financing"])
    code = StringType(required=True, choices=["prepayment", "postpayment"])
    percentage = FloatType(required=True, max_value=100, validators=[is_positive_float])

    duration = ModelType(Duration, required=True)
    sequenceNumber = IntType(required=True, min_value=0)
    relatedLot = MD5Type()

    def validate_relatedLot(self, data, value):
        tender = data["__parent__"]
        if value is not None and value not in [l.get("id") for l in getattr(tender, "lots", [])]:
            raise ValidationError(u"relatedLot should be one of the lots.")

    def validate_description(self, data, value):
        if data.get("title", "") == "anotherEvent" and not value:
            raise ValidationError(u"This field is required.")

        should_validate = get_first_revision_date(data["__parent__"], default=get_now()) > MILESTONES_VALIDATION_FROM
        if should_validate and value and len(value) > 2000:
            raise ValidationError("description should contain at most 2000 characters")


class PlanRelation(Model):
    id = MD5Type(required=True)

    class Options:
        roles = {
            "create": whitelist("id"),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }


@implementer(ITender)
class BaseTender(OpenprocurementSchematicsDocument, Model):
    class Options:
        namespace = "Tender"
        _edit_role = whitelist(
            "awardCriteriaDetails_ru",
            "procurementMethodRationale_en",
            "eligibilityCriteria",
            "eligibilityCriteria_ru",
            "awardCriteriaDetails_en",
            "description",
            "milestones",
            "buyers",
            "procurementMethodRationale_ru",
            "description_en",
            "mainProcurementCategory",
            "procurementMethodDetails",
            "title",
            "awardCriteriaDetails",
            "submissionMethodDetails_en",
            "title_ru",
            "procurementMethodRationale",
            "eligibilityCriteria_en",
            "description_ru",
            "funders",
            "submissionMethodDetails_ru",
            "title_en",
            "submissionMethodDetails",
        )
        _create_role = _edit_role + whitelist("mode", "procurementMethodType")
        roles = {
            "create": _create_role,
            "edit_draft": whitelist("status"),
            "edit": _edit_role,
            "view": _create_role
            + whitelist(
                "date",
                "awardCriteria",
                "tenderID",
                "documents",
                "doc_id",
                "submissionMethod",
                "dateModified",
                "status",
                "procurementMethod",
                "owner",
                "plans",
                "criteria",
            ),
            "auction_view": whitelist(
                "tenderID",
                "dateModified",
                "bids",
                "items",
                "auctionPeriod",
                "minimalStep",
                "auctionUrl",
                "features",
                "lots",
            ),
            "auction_post": whitelist("bids"),
            "auction_patch": whitelist("auctionUrl", "bids", "lots"),
            "chronograph": whitelist("auctionPeriod", "lots", "next_check"),
            "chronograph_view": whitelist(
                "status",
                "enquiryPeriod",
                "tenderPeriod",
                "auctionPeriod",
                "awardPeriod",
                "awards",
                "lots",
                "doc_id",
                "submissionMethodDetails",
                "mode",
                "numberOfBids",
                "complaints",
            ),
            "Administrator": whitelist("status", "mode", "procuringEntity", "auctionPeriod", "lots"),
            "listing": whitelist("dateModified", "doc_id"),
            "contracting": whitelist("doc_id", "owner"),
            "embedded": blacklist("_id", "_rev", "doc_type", "__parent__"),
            "default": blacklist("doc_id", "__parent__"),  # obj.store() use default role
            "plain": blacklist(  # is used for getting patches
                "_attachments", "revisions", "dateModified", "_id", "_rev", "doc_type", "__parent__"
            ),
        }

    title = StringType(required=True)
    title_en = StringType()
    title_ru = StringType()
    documents = ListType(
        ModelType(Document, required=True), default=list()
    )  # All documents and attachments related to the tender.
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    date = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    tenderID = (
        StringType()
    )  # TenderID should always be the same as the OCID. It is included to make the flattened data structure more convenient.
    owner = StringType()
    owner_token = StringType()
    transfer_token = StringType()
    mode = StringType(choices=["test"])
    procurementMethodRationale = (
        StringType()
    )  # Justification of procurement method, especially in the case of Limited tendering.
    procurementMethodRationale_en = StringType()
    procurementMethodRationale_ru = StringType()
    if SANDBOX_MODE:
        procurementMethodDetails = StringType()
    funders = ListType(
        ModelType(Organization, required=True), validators=[validate_funders_unique, validate_funders_ids]
    )
    mainProcurementCategory = StringType(choices=["goods", "services", "works"])
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq, validate_milestones])
    buyers = ListType(ModelType(BaseOrganization, required=True), default=list())
    plans = ListType(ModelType(PlanRelation, required=True), default=list())

    def link_plan(self, plan_id):
        self.plans.append(PlanRelation({"id": plan_id}))

    def validate_plans(self, data, value):
        if len(set(i["id"] for i in value)) < len(value):
            raise ValidationError("The list should not contain duplicates")
        if len(value) > 1 and data.get("procuringEntity", {}).get("kind", "") != "central":
            raise ValidationError("Linking more than one plan is allowed only if procuringEntity.kind is 'central'")

    _attachments = DictType(DictType(BaseType), default=dict())  # couchdb attachments
    revisions = ListType(ModelType(Revision, required=True), default=list())

    def __repr__(self):
        return "<%s:%r@%r>" % (type(self).__name__, self.id, self.rev)

    def __local_roles__(self):
        roles = dict([("{}_{}".format(self.owner, self.owner_token), "tender_owner")])
        return roles

    @serializable(serialized_name="id")
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.
        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [
            k for k in data.keys() if data[k] == self.__class__.fields[k].default or data[k] == getattr(self, k)
        ]
        for k in del_keys:
            del data[k]

        self._data.update(data)
        return self

    def validate_procurementMethodDetails(self, *args, **kw):
        if self.mode and self.mode == "test" and self.procurementMethodDetails and self.procurementMethodDetails != "":
            raise ValidationError(u"procurementMethodDetails should be used with mode test")

    def validate_mainProcurementCategory(self, data, value):
        validation_date = get_first_revision_date(data, default=get_now())
        if validation_date >= MPC_REQUIRED_FROM and value is None:
            raise ValidationError(BaseType.MESSAGES["required"])

    def validate_milestones(self, data, value):
        required = get_first_revision_date(data, default=get_now()) > MILESTONES_VALIDATION_FROM
        if required and (value is None or len(value) < 1):
            raise ValidationError("Tender should contain at least one milestone")

    def validate_buyers(self, data, value):
        if data.get("procuringEntity", {}).get("kind", "") == "central" and not value:
            raise ValidationError(BaseType.MESSAGES["required"])

    def _acl_cancellation(self, acl):
        acl.extend(
            [(Allow, "{}_{}".format(self.owner, self.owner_token), "edit_cancellation")]
        )

        old_rules = get_first_revision_date(self, default=get_now()) < RELEASE_2020_04_19

        accept_tender = all([
            any([j.status == "resolved" for j in i.complaints])
            for i in self.cancellations
            if i.status == "unsuccessful" and getattr(i, "complaints", None) and not i.relatedLot
        ])

        if (
            old_rules
            or (not any([i.status == "pending" and not i.relatedLot for i in self.cancellations])
                and accept_tender)
        ):
            acl.extend(
                [
                    (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_tender"),
                    (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_tender_documents"),
                ]
            )

    def _acl_cancellation_complaint(self, acl):

        self._acl_cancellation(acl)

        if self.status == "active.tendering":
            acl_cancellation_complaints = [
                (Allow, "g:brokers", "create_cancellation_complaint"),
            ]
        else:
            acl_cancellation_complaints = [
                (Allow, "{}_{}".format(i.owner, i.owner_token), "create_cancellation_complaint")
                for i in self.bids
            ]

        acl.extend(acl_cancellation_complaints)

    def append_award(self, bid,  all_bids, lot_id=None):
        now = get_now()
        award_data = {
            "bid_id": bid["id"],
            "lotID": lot_id,
            "status": "pending",
            "date": now,
            "value": bid["value"],
            "suppliers": bid["tenderers"],
        }
        # append an "alp" milestone if it's the case
        award_class = self.__class__.awards.model_class
        if hasattr(award_class, "milestones"):
            award_data["milestones"] = prepare_award_milestones(self, bid, all_bids, lot_id)

        award = award_class(award_data)
        award.__parent__ = self
        self.awards.append(award)


class Tender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""

    procurementMethod = StringType(
        choices=["open", "selective", "limited"], default="open"
    )  # Specify tendering method as per GPA definitions of Open, Selective, Limited (http://www.wto.org/english/docs_e/legal_e/rev-gpr-94_01_e.htm)
    awardCriteria = StringType(
        choices=["lowestCost", "bestProposal", "bestValueToGovernment", "singleBidOnly"], default="lowestCost"
    )  # Specify the selection criteria, by lowest cost,
    awardCriteriaDetails = StringType()  # Any detailed or further information on the selection criteria.
    awardCriteriaDetails_en = StringType()
    awardCriteriaDetails_ru = StringType()
    submissionMethod = StringType(
        choices=["electronicAuction", "electronicSubmission", "written", "inPerson"], default="electronicAuction"
    )  # Specify the method by which bids must be submitted, in person, written, or electronic auction
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    eligibilityCriteria = StringType()  # A description of any eligibility criteria for potential suppliers.
    eligibilityCriteria_en = StringType()
    eligibilityCriteria_ru = StringType()
    status = StringType(
        choices=[
            "draft",
            "active.enquiries",
            "active.tendering",
            "active.auction",
            "active.qualification",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
        ],
        default="active.enquiries",
    )

    criteria = ListType(ModelType(Criterion, required=True), default=list())

    create_accreditations = (ACCR_1, ACCR_5)
    central_accreditations = (ACCR_5,)
    edit_accreditations = (ACCR_2,)

    __name__ = ""

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
            ]
        )
        self._acl_cancellation_complaint(acl)
        return acl
