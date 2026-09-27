import logging
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from hashlib import sha512

from pyramid.interfaces import IAuthenticationPolicy
from schematics.exceptions import ValidationError
from schematics.types import (
    BaseType,
    BooleanType,
    DateTimeType,
    DecimalType,
    IntType,
    StringType,
)

from openprocurement.api.auth import AccreditationLevel, extract_access_token
from openprocurement.api.constants import (
    ATC_SCHEME,
    CCCE_UA_SCHEME,
    CPV_PHARM_PREFIX,
    CPV_PHARM_PRODUCTS,
    FUNDERS,
    GMDN_2019_SCHEME,
    GMDN_2023_SCHEME,
    GMDN_CPV_PREFIXES,
    INN_SCHEME,
    UA_ROAD_CPV_PREFIXES,
    UA_ROAD_SCHEME,
)
from openprocurement.api.constants_env import (
    CONFIDENTIAL_EDRPOU_LIST,
    CONTRACT_OWNER_REQUIRED_FROM,
    CONTRACT_OWNER_REQUIRED_FROM_BY_EDRPOU,
    ITEMS_UNIT_VALUE_AMOUNT_VALIDATION_FROM,
    ITEMS_UNIT_VALUE_AMOUNT_VAT_AWARE_VALIDATION_FROM,
    MILESTONES_VALIDATION_FROM,
    PQ_CRITERIA_ID_FROM,
    RELEASE_ECRITERIA_ARTICLE_17,
    REQUIRED_DELIVERY_AND_FINANCING_MILESTONES_VALIDATION_FROM,
    TENDER_SIGNER_INFO_REQUIRED_FROM,
    UNIT_PRICE_REQUIRED_FROM,
)
from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.document import ConfidentialityType
from openprocurement.api.procedure.utils import is_item_owner, is_obj_const_active, to_decimal
from openprocurement.api.utils import (
    error_handler,
    get_first_revision_date,
    is_gmdn_classification,
    is_ua_road_classification,
    raise_operation_error,
    request_fetch_root_tender_for_tender,
)
from openprocurement.api.validation import validate_tender_first_revision_date
from openprocurement.tender.core.constants import (
    AMOUNT_NET_COEF,
    ReqStatuses,
    TenderMilestoneType,
)
from openprocurement.tender.core.procedure.utils import (
    find_item_by_id,
    find_lot,
    is_multi_currency_tender,
    prepare_shortlisted_firms_author_key,
    prepare_shortlisted_firms_keys,
    tender_created_after,
    tender_created_before,
)
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.pricequotation.constants import PQ_PROFILE_PATTERN as PQ_PROFILE_PATTERN

LOGGER = logging.getLogger(__name__)
OPERATIONS = {"POST": "add", "PATCH": "update", "PUT": "update", "DELETE": "delete"}


def validate_dialogue_owner(request, **_):
    item = request.validated["tender"]
    acc_token = extract_access_token(request)
    acc_token_hex = sha512(acc_token.encode("utf-8")).hexdigest()
    if request.authenticated_userid != item["owner"] or acc_token_hex != item["dialogue_token"]:
        raise_operation_error(request, "Forbidden", location="url", name="permission")


def unless_bots_or_auction(*validations):
    def decorated(request, **_):
        if request.authenticated_role not in ("bots", "auction"):
            for validation in validations:
                validation(request)

    return decorated


def validate_lotvalue_value(tender, related_lot, value):
    lot = find_lot(tender, related_lot)
    if lot and value:
        tender_lot_value = lot.get("value")
        if tender["config"]["valueCurrencyEquality"]:
            validate_lot_value_currency(tender_lot_value, value)
            if tender["config"]["hasValueRestriction"]:
                validate_lot_value_amount(tender_lot_value, value)
        validate_lot_value_vat(tender_lot_value, value)


def validate_lot_value_amount(tender_lot_value, value):
    if float(tender_lot_value["amount"]) < value["amount"]:
        raise ValidationError("value of bid should be less than value of lot")


def validate_lot_value_currency(tender_lot_value, value, name="value"):
    if tender_lot_value["currency"] != value["currency"]:
        raise ValidationError(f"currency of bid should be identical to currency of {name} of lot")


def validate_lot_value_vat(tender_lot_value, value, name="value"):
    if tender_lot_value["valueAddedTaxIncluded"] != value["valueAddedTaxIncluded"]:
        raise ValidationError(
            f"valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of {name} of lot"
        )


def validate_related_lot(tender, related_lot):
    if related_lot not in [lot["id"] for lot in tender.get("lots") or [] if lot]:
        raise ValidationError("relatedLot should be one of lots")


# bids req response
def base_validate_operation_ecriteria_objects(request, valid_statuses="", obj_name="tender"):
    validate_tender_first_revision_date(request, validation_date=RELEASE_ECRITERIA_ARTICLE_17)
    current_status = request.validated[obj_name]["status"]
    if current_status not in valid_statuses:
        raise_operation_error(
            request,
            "Can't {} object if {} not in {} statuses".format(request.method.lower(), obj_name, valid_statuses),
        )


# auction
def validate_auction_tender_status(request, **_):
    tender_status = request.validated["tender"]["status"]
    if tender_status != "active.auction":
        operations = {
            "GET": "get auction info",
            "POST": "report auction results",
            "PATCH": "update auction urls",
        }
        raise_operation_error(
            request,
            f"Can't {operations[request.method]} in current ({tender_status}) tender status",
        )


def get_award_document_role(request):
    tender = request.validated["tender"]
    if is_item_owner(request, tender):
        role = "tender_owner"
    else:
        role = request.authenticated_role
    return role


# TENDER
def get_tender_document_role(request):
    tender = request.validated["tender"]
    if is_item_owner(request, tender):
        role = "tender_owner"
    else:
        role = request.authenticated_role
    return role


# QUALIFICATION
# QUALIFICATION DOCUMENT
def get_qualification_document_role(request):
    tender = request.validated["tender"]
    if is_item_owner(request, tender):
        role = "tender_owner"
    else:
        role = request.authenticated_role
    return role


# lot


def is_positive_float(value):
    if value <= 0:
        raise ValidationError("Float value should be greater than 0.")


def check_requirements_active(criterion):
    for rg in criterion.get("requirementGroups", []):
        for requirement in rg.get("requirements", []):
            if requirement.get("status", "") == "active":
                return True
    return False


TYPEMAP = {
    "string": StringType(),
    "integer": IntType(),
    "number": DecimalType(),
    "boolean": BooleanType(),
    "date-time": DateTimeType(),
}


def validate_value_factory(type_map):
    def validator(value, datatype):
        if value is None:
            return
        type_ = type_map.get(datatype)
        if not type_:
            raise ValidationError("Type mismatch: value {} does not confront type {}".format(value, type_))
        return type_.to_native(value)

    return validator


validate_value_type = validate_value_factory(TYPEMAP)


def validate_gmdn(classification_id, additional_classifications):
    gmdn_count = sum(1 for i in additional_classifications if i["scheme"] in (GMDN_2023_SCHEME, GMDN_2019_SCHEME))
    if is_gmdn_classification(classification_id):
        inn_anc_count = sum(1 for i in additional_classifications if i["scheme"] in [INN_SCHEME, ATC_SCHEME])
        if 0 not in [inn_anc_count, gmdn_count]:
            raise ValidationError(
                "Item shouldn't have additionalClassifications with both schemes {}/{} and {}".format(
                    INN_SCHEME, ATC_SCHEME, GMDN_2019_SCHEME
                )
            )
        if gmdn_count > 1:
            raise ValidationError(
                "Item shouldn't have more than 1 additionalClassification with scheme {}".format(GMDN_2019_SCHEME)
            )
    elif gmdn_count != 0:
        raise ValidationError(
            "Item shouldn't have additionalClassification with scheme {} for cpv not starts with {}".format(
                GMDN_2019_SCHEME, ", ".join(GMDN_CPV_PREFIXES)
            )
        )


def validate_ua_road(classification_id, additional_classifications):
    road_count = sum(1 for i in additional_classifications if i["scheme"] == UA_ROAD_SCHEME)
    if is_ua_road_classification(classification_id):
        if road_count > 1:
            raise ValidationError(
                "Item shouldn't have more than 1 additionalClassification with scheme {}".format(UA_ROAD_SCHEME)
            )
    elif road_count != 0:
        raise ValidationError(
            "Item shouldn't have additionalClassification with scheme {} for cpv not starts with {}".format(
                UA_ROAD_SCHEME, ", ".join(UA_ROAD_CPV_PREFIXES)
            )
        )


def validate_ccce_ua(additional_classifications):
    ccce_count = sum(1 for i in additional_classifications if i["scheme"] == CCCE_UA_SCHEME)
    if ccce_count > 1:
        raise ValidationError(
            f"Object shouldn't have more than 1 additionalClassification with scheme {CCCE_UA_SCHEME}"
        )


def validate_funders_ids(funders, *args):
    for funder in funders:
        if funder.identifier and (funder.identifier.scheme, funder.identifier.id) not in FUNDERS:
            raise ValidationError("Funder identifier should be one of the values allowed")


def validate_object_id_uniq(objs, *_, obj_name=None):
    if objs:
        if not obj_name:
            obj_name = objs[0].__class__.__name__
        obj_name_multiple = obj_name[0].lower() + obj_name[1:]
        ids = [i["id"] for i in objs]
        if ids and len(set(ids)) != len(ids):
            raise ValidationError("{} id should be uniq for all {}s".format(obj_name, obj_name_multiple))


def get_items_unit_value_amounts(items):
    # unit value amount of an item is its price per unit multiplied by the quantity
    return [
        to_decimal(item["quantity"]) * to_decimal(item["unit"]["value"]["amount"])
        for item in items
        if item.get("quantity") is not None and item.get("unit", {}).get("value")
    ]


def validate_items_unit_amount(items_unit_value_amount, obj, obj_name="contract"):
    obj_value = obj.get("value")

    if is_multi_currency_tender():
        # Skip validation for multi-currency tenders
        # It can have different currencies across lots, units, bids etc.
        return

    if not items_unit_value_amount or not obj_value or obj_value.get("amount") is None:
        # Skip. Nothing to compare
        return

    vat_aware_validation = tender_created_after(ITEMS_UNIT_VALUE_AMOUNT_VAT_AWARE_VALIDATION_FROM)
    if get_tender().get("procurementMethodType") == PQ:
        vat_aware_validation = tender_created_after(ITEMS_UNIT_VALUE_AMOUNT_VALIDATION_FROM)

    units_amount_sum = sum(items_unit_value_amount)
    obj_amount = to_decimal(obj_value["amount"])

    # New validation rules
    if vat_aware_validation:
        # VAT-inclusive: unit sum between net and gross;
        # VAT-exclusive: must equal amount;
        tax_included = obj_value["valueAddedTaxIncluded"]
        if tax_included:
            # obj.value.amountNet or amount-20%
            obj_amount_net = obj_value.get("amountNet", obj_amount / AMOUNT_NET_COEF)
            # ignore coins for this validation
            if units_amount_sum <= 0 or not (int(obj_amount_net) <= int(units_amount_sum) <= int(obj_amount)):
                raise_operation_error(
                    get_request(),
                    f"Total amount of unit values must be no more than {obj_name}.value.amount and no less than net {obj_name} amount",
                    name="items",
                    status=422,
                )
        elif int(obj_amount) != int(units_amount_sum):  # ignore coins
            raise_operation_error(
                get_request(),
                f"Total amount of unit values should be equal {obj_name}.value.amount if VAT is not included in {obj_name}",
                name="items",
                status=422,
            )

    # Legacy validation rules
    if not vat_aware_validation:
        # Upper bound only.
        if not (int(units_amount_sum) <= int(obj_amount)):  # pylint: disable=unnecessary-negation
            raise_operation_error(
                get_request(),
                f"Total amount of unit values can't be greater than {obj_name}.value.amount",
                name="items",
                status=422,
            )


def validate_numerated(field_name="sequenceNumber"):
    def validator(value):
        if not value:
            return
        for i, obj in enumerate(value):
            if obj.get(field_name) is not None and obj.get(field_name) != i + 1:  # field can be optional
                raise ValidationError(
                    f"Field {field_name} should contain incrementing sequence numbers starting from 1"
                )

    return validator


def validate_doc_type_quantity(documents, document_type="notice", obj_name="tender"):
    """
    Check whether there is no more than one document in list with particular documentType.
    If there is more than one document the error will be raised.
    :param documents: list of documents
    :param document_type: type of document
    :param obj_name: name of object
    """
    grouped_docs = defaultdict(set)
    new_doc_versions = set()
    for doc in reversed(documents):
        if doc.get("documentType") == document_type and doc["id"] not in new_doc_versions:
            grouped_docs[doc.get("relatedItem")].add(doc["id"])
        new_doc_versions.add(doc["id"])
    for lot, docs in grouped_docs.items():
        if len(docs) > 1:
            raise_operation_error(
                get_request(),
                f"{document_type} document in {obj_name} should be only one{f' for lot {lot}' if lot else ''}",
                name="documents",
                status=422,
            )


def validate_doc_type_required(documents, document_type="notice", document_of=None, after_date=None):
    """
    Check whether there is document in list which is required.
    If there is no document the error will be raised.
    :param documents: list of documents
    :param document_type: type of document
    :param document_of: str. What kind of object doc relates to
    :param after_date: date after which document should be published
    """
    new_doc_versions = set()
    for doc in reversed(documents):
        if (
            doc["id"] not in new_doc_versions
            and doc.get("documentType") == document_type
            and doc["title"][-4:] == ".p7s"
            and doc.get("documentOf") == document_of
            and (
                after_date is None
                or datetime.fromisoformat(doc.get("datePublished")) > datetime.fromisoformat(after_date)
            )
        ):
            break
        new_doc_versions.add(doc["id"])
    else:
        raise_operation_error(
            get_request(),
            f"Document with type '{document_type}' and format pkcs7-signature is required",
            status=422,
            name="documents",
        )


def validate_edrpou_confidentiality_doc(doc, should_be_public=False):
    tender = get_tender()
    if (
        not should_be_public
        and doc.get("title") == "sign.p7s"
        and doc.get("format") == "application/pkcs7-signature"
        and doc.get("author", "tender_owner") == "tender_owner"
        and tender.get("procuringEntity", {}).get("identifier", {}).get("id") in CONFIDENTIAL_EDRPOU_LIST
    ):
        if doc.get("confidentiality", ConfidentialityType.BUYER_ONLY) != ConfidentialityType.BUYER_ONLY:
            raise_operation_error(
                get_request(),
                "Document should be confidential",
                name="confidentiality",
                status=422,
            )
    elif doc.get("confidentiality") == ConfidentialityType.BUYER_ONLY:
        raise_operation_error(
            get_request(),
            "Document should be public",
            name="confidentiality",
            status=422,
        )


def validate_required_fields(request, data: dict, required_fields: dict, name="data"):
    """
    Validates that all required fields are present in the given data, including nested fields.

    Args:
        data (dict): The dictionary to validate.
        required_fields (dict): A dictionary where keys are field names and values are:
            - `True`: Field is required.
            - `False`: Field is optional.
            - A dictionary for nested fields, optionally with `__required__`.

    Returns:
        dict: A nested dictionary of missing fields with their respective error messages.
    """

    def validation(data: dict, required_fields: dict):
        errors = {}
        for field, rules in required_fields.items():
            # Determine if the field itself is required
            if isinstance(rules, bool):  # Simple required/optional case
                is_required = rules
                nested_rules = {}
            elif isinstance(rules, dict):  # Nested rules or explicit "__required__"
                is_required = rules.get("__required__", True)
                nested_rules = {k: v for k, v in rules.items() if k != "__required__"}
            else:
                continue  # Ignore invalid rule definitions

            # Check if the field is missing or None
            if field not in data or data[field] is None:
                if is_required:
                    errors[field] = BaseType.MESSAGES["required"]
                continue

            # Validate nested fields if present
            if nested_rules:
                if isinstance(data[field], dict):  # Validate nested dict
                    nested_errors = validation(data[field], nested_rules)
                    if nested_errors:
                        errors[field] = nested_errors
                elif isinstance(data[field], list):  # Validate list of nested dicts
                    list_errors = {}
                    for i, item in enumerate(data[field]):
                        if isinstance(item, dict):
                            item_errors = validation(item, nested_rules)
                            if item_errors:
                                list_errors[i] = item_errors
                        else:
                            list_errors[i] = BaseType.MESSAGES["required"]
                    if list_errors:
                        errors[field] = list_errors

        return errors

    errors = validation(data, required_fields)
    if errors:
        raise_operation_error(request, errors, name=name, status=422)


def validate_field_change(field_name, before_obj, after_obj, validator, args):
    """
    Call validator if field change during PATCH

    Args:
        field_name (str): Name of field.
        before_obj (dict): Object before PATCH
        after_obj (dict): Object after PATCH
        validator (callable): Validation method if field has been changed
        args (tuple): Tuple of arguments for validator function
    """
    if before_obj.get(field_name) != after_obj.get(field_name):
        validator(*args)


def validate_econtract_fields_tender(request, tender):
    if buyers := tender.get("buyers", []):
        validate_buyers_contract_owner_consistent(request, buyers)
        for index, buyer in enumerate(buyers):
            validate_signer_info(request, tender, buyer, "buyers", index)
            validate_contract_owner_required(request, tender, buyer, "buyers", index)
            validate_contract_owner(request, tender, buyer, "buyers", index)
    else:
        procuring_entity = tender.get("procuringEntity", {})
        validate_signer_info(request, tender, procuring_entity, "procuringEntity")
        validate_contract_owner_required(request, tender, procuring_entity, "procuringEntity")
        validate_contract_owner(request, tender, procuring_entity, "procuringEntity")


def validate_econtract_fields_bid(request, tender, bid):
    tenderers = bid.get("tenderers", [])
    for index, tenderer in enumerate(tenderers):
        validate_signer_info(request, tender, tenderer, "tenderers", index)
        validate_contract_owner_consistent(request, tender, tenderer, "tenderers", index)
        validate_contract_owner(request, tender, tenderer, "tenderers", index)


def validate_econtract_fields_award(request, tender, award):
    suppliers = award.get("suppliers", [])
    for index, supplier in enumerate(suppliers):
        validate_signer_info(request, tender, supplier, "suppliers", index)
        validate_contract_owner_consistent(request, tender, supplier, "suppliers", index)
        validate_contract_owner(request, tender, supplier, "suppliers", index)


def validate_signer_info(request, tender, organization, field_name, field_index=None) -> None:
    signer_info = organization.get("signerInfo")
    contract_template_name = tender.get("contractTemplateName")
    field_path = f"{field_name}.{field_index}" if field_index is not None else field_name
    if tender_created_after(TENDER_SIGNER_INFO_REQUIRED_FROM) and contract_template_name and not signer_info:
        raise_operation_error(
            request,
            {"signerInfo": BaseType.MESSAGES["required"]},
            name=field_path,
            status=422,
        )


def validate_contract_owner(request, tender, organization, field_name, field_index=None) -> None:
    contract_owner = organization.get("contract_owner")
    contract_template_name = tender.get("contractTemplateName")
    field_path = f"{field_name}.{field_index}" if field_index is not None else field_name
    if contract_owner is not None:
        if not contract_template_name:
            raise_operation_error(
                request,
                {"contract_owner": "could be set only along with contractTemplateName"},
                name=field_path,
                status=422,
            )
        if contract_owner not in get_contract_owner_choices():
            raise_operation_error(
                request,
                {"contract_owner": "should be one of brokers with level 6"},
                name=field_path,
                status=422,
            )


def validate_contract_owner_required(request, tender, organization, field_name, field_index=None) -> None:
    contract_owner = organization.get("contract_owner")
    field_path = f"{field_name}.{field_index}" if field_index is not None else field_name
    mode = tender.get("mode")
    contract_template_name = tender.get("contractTemplateName")

    edrpou_id = organization.get("identifier", {}).get("id")
    edrpou_from = CONTRACT_OWNER_REQUIRED_FROM_BY_EDRPOU.get(edrpou_id) if edrpou_id else None
    required_from = edrpou_from or CONTRACT_OWNER_REQUIRED_FROM

    # For test mode, we don't require contract owner, it is optional
    if mode == "test":
        return

    # For old tenders, it is forbidden to set contract owner unless it is test mode tender
    if tender_created_before(required_from):
        if contract_owner is not None:
            raise_operation_error(
                request,
                {"contract_owner": "Rogue field"},
                name=field_path,
                status=422,
            )
        return

    # Otherwise, we require contract owner if contractTemplateName is set
    if contract_owner is None and contract_template_name:
        raise_operation_error(
            request,
            {"contract_owner": BaseType.MESSAGES["required"]},
            name=field_path,
            status=422,
        )


def validate_contract_owner_consistent(request, tender, organization, field_name, field_index=None) -> None:
    if buyers := tender.get("buyers", []):
        tender_has_contract_owner = any(buyer.get("contract_owner") is not None for buyer in buyers)
    else:
        procuring_entity = tender.get("procuringEntity", {})
        tender_has_contract_owner = procuring_entity.get("contract_owner") is not None

    contract_owner = organization.get("contract_owner")
    field_path = f"{field_name}.{field_index}" if field_index is not None else field_name
    if not tender_has_contract_owner and contract_owner is not None:
        raise_operation_error(
            request,
            {"contract_owner": "could not be set when contract_owner is not set on tender"},
            name=field_path,
            status=422,
        )
    elif tender_has_contract_owner and contract_owner is None:
        raise_operation_error(
            request,
            {"contract_owner": "should be set when contract_owner is set on tender"},
            name=field_path,
            status=422,
        )


def validate_buyers_contract_owner_consistent(request, buyers) -> None:
    if not any(buyer.get("contract_owner") is not None for buyer in buyers):
        return
    for index, buyer in enumerate(buyers):
        if buyer.get("contract_owner") is None:
            raise_operation_error(
                request,
                {"contract_owner": "should be set for all buyers when set on any buyer"},
                name=f"buyers.{index}",
                status=422,
            )


def get_contract_owner_choices():
    request = get_request()
    policy = request.registry.queryUtility(IAuthenticationPolicy)
    users = []
    for user in policy.users.values():
        if user["group"] == "brokers" and AccreditationLevel.ACCR_6 in user["level"]:
            users.append(user["name"])
    return users


def validate_milestone_duration_days(tender, milestone):
    """
    Function for validating milestone.duration.days for financing/delivery milestones
    """
    if (
        milestone.get("type") in ("financing", "delivery")
        and get_first_revision_date(tender, default=get_request_now()) > MILESTONES_VALIDATION_FROM
        and milestone.get("duration", {}).get("days", 0) > 1000
    ):
        raise_operation_error(
            get_request(),
            [{"duration": [f"days shouldn't be more than 1000 for {milestone.get('type')} milestone"]}],
            status=422,
            name="milestones",
        )


def validate_milestone_sums(milestones):
    """
    Function for validating milestone.percentage sums to be equal to 100, data is grouped by relatedLot
    """
    sums = {
        "financing": defaultdict(Decimal),
        "delivery": defaultdict(Decimal),
    }
    for milestone in milestones:
        sums[milestone["type"]][milestone.get("relatedLot")] += to_decimal(milestone.get("percentage", 0))

    for milestone_type, values in sums.items():
        for uid, sum_value in values.items():
            if sum_value != Decimal("100"):
                raise_operation_error(
                    get_request(),
                    f"Sum of the {milestone_type} milestone percentages {sum_value} "
                    f"is not equal 100{f' for lot {uid}' if uid else ''}.",
                    status=422,
                    name="milestones",
                )


def validate_milestones_sequence_number(
    milestones,
    error_msg="Field should contain incrementing sequence numbers starting from 1",
):
    """
    Function for validating milestone.sequenceNumber
    """
    for i, milestone in enumerate(milestones, 1):
        if milestone.get("sequenceNumber") != i:
            raise_operation_error(
                get_request(),
                [{"sequenceNumber": error_msg}],
                status=422,
                name="milestones",
            )


def validate_value_vat_disabled(request, value, field_name, date_from):
    if value.get("valueAddedTaxIncluded") is not True:
        return

    # for 2-stage procedures value is inherited from the 1st stage,
    # so the feature has to be checked against the root tender
    request_fetch_root_tender_for_tender(request, request.validated["tender"]["_id"], raise_error=False)
    root_tender = request.validated.get("root_tender") or request.validated["tender"]

    if tender_created_after(date_from, root_tender):
        raise_operation_error(
            request,
            "valueAddedTaxIncluded should be false",
            status=422,
            location="body",
            name=f"{field_name}.valueAddedTaxIncluded",
        )


def validate_items_required_fields(request, items, delivery=False, unit=True, quantity=True):
    """
    Replaces model-level requirements that used to differ between procedures' Item models:
    `unit` (Item.validate_unit), `quantity` (BaseItem.validate_quantity, UNIT_PRICE_REQUIRED_FROM),
    `deliveryDate` (PeriodEndRequired) and `deliveryAddress`. Produces the same 422 shape schematics did.
    """
    quantity = quantity and is_obj_const_active(get_tender(), UNIT_PRICE_REQUIRED_FROM)
    errors = []
    for item in items or []:
        item_errors = {}
        if unit and not item.get("unit"):
            item_errors["unit"] = [BaseType.MESSAGES["required"]]
        if quantity and item.get("quantity") is None:
            item_errors["quantity"] = [BaseType.MESSAGES["required"]]
        if delivery:
            delivery_date = item.get("deliveryDate")
            if delivery_date is None:
                item_errors["deliveryDate"] = [BaseType.MESSAGES["required"]]
            elif not delivery_date.get("endDate"):
                item_errors["deliveryDate"] = {"endDate": [BaseType.MESSAGES["required"]]}
            if item.get("deliveryAddress") is None:
                item_errors["deliveryAddress"] = [BaseType.MESSAGES["required"]]
        if item_errors:
            errors.append(item_errors)
    if errors:
        raise_operation_error(request, errors, status=422, name="items")


def validate_esco_lotvalue_value(tender, related_lot, value):
    if not related_lot:
        return
    if tender.get("status") in ("invalid", "deleted", "draft"):
        return
    lot = find_lot(tender, related_lot)
    if lot and value:
        tender_lot_value = lot.get("minValue")
        validate_lot_value_currency(tender_lot_value, value, name="minValue")
        validate_lot_value_vat(tender_lot_value, value, name="minValue")


def validate_required_nested_fields(request, data, required_fields):
    """
    Replacement for procedure-specific `required=True` (and `min_length=1`) declared on models.

    `required_fields` is a dict {field: True | nested dict}. A nested dict is applied to a dict value
    or to every element of a list value. Produces the same 422 shape schematics produces for models:
    one error per top-level field, nested dicts for ModelType, list of dicts (failed items only) for ListType.
    """

    def _validate(obj, spec):
        errors = {}
        for field, rules in spec.items():
            value = obj.get(field)
            if isinstance(rules, dict):
                if isinstance(value, list):
                    list_errors = [e for e in (_validate(i, rules) for i in value if isinstance(i, dict)) if e]
                    if list_errors:
                        errors[field] = list_errors
                elif isinstance(value, dict):
                    nested_errors = _validate(value, rules)
                    if nested_errors:
                        errors[field] = nested_errors
            elif rules:
                if value is None:
                    errors[field] = [BaseType.MESSAGES["required"]]
                elif value == "":
                    errors[field] = [StringType.MESSAGES["min_length"]]
        return errors

    errors = _validate(data, required_fields)
    if errors:
        for field, messages in errors.items():
            request.errors.add("body", field, messages)
        request.errors.status = 422
        raise error_handler(request)


# --- priceQuotation ---


def validate_pq_profile_pattern(profile):
    result = PQ_PROFILE_PATTERN.findall(profile)
    if len(result) != 1:
        raise ValidationError("The profile value doesn't match id pattern")


def validate_pq_criteria_id_uniq(objs, *args):
    if not objs:
        return
    tender = get_tender()
    if get_first_revision_date(tender, default=get_request_now()) > PQ_CRITERIA_ID_FROM:
        ids = [i.id for i in objs]
        if len(set(ids)) != len(ids):
            raise ValidationError("Criteria id should be uniq")

        rg_ids = [rg.id for c in objs for rg in c.requirementGroups or ""]
        if len(rg_ids) != len(set(rg_ids)):
            raise ValidationError("Requirement group id should be uniq in tender")

        req_ids = [req.id for c in objs for rg in c.requirementGroups or "" for req in rg.requirements or ""]
        if len(req_ids) != len(set(req_ids)):
            raise ValidationError("Requirement id should be uniq for all requirements in tender")

        for criterion in objs:
            for rg in criterion.requirementGroups or "":
                req_titles = [req.title for req in rg.requirements or "" if req.status == ReqStatuses.ACTIVE]
                if len(set(req_titles)) != len(req_titles):
                    raise ValidationError("Requirement title should be uniq for one requirementGroup")


def validate_items_classification_id(request, items):
    """former validate_classification_id list validator of tender models (pharm products / INN rule)"""
    for item in items or []:
        schemes = [x.get("scheme") for x in item.get("additionalClassifications") or []]
        schemes_inn_count = schemes.count(INN_SCHEME)
        classification_id = (item.get("classification") or {}).get("id") or ""
        if classification_id == CPV_PHARM_PRODUCTS and schemes_inn_count != 1:
            raise_operation_error(
                request,
                [
                    "Item with classification.id={} have to contain exactly one additionalClassifications "
                    "with scheme={}".format(CPV_PHARM_PRODUCTS, INN_SCHEME)
                ],
                status=422,
                name="items",
            )
        if classification_id.startswith(CPV_PHARM_PREFIX) and schemes_inn_count > 1:
            raise_operation_error(
                request,
                [
                    "Item with classification.id that starts with {} and contains additionalClassification "
                    "objects have to contain no more than one additionalClassifications "
                    "with scheme={}".format(CPV_PHARM_PREFIX, INN_SCHEME)
                ],
                status=422,
                name="items",
            )


def validate_tender_milestones_required(request, tender, required=True, delivery_financing=True):
    """former TenderMilestoneMixin.validate_milestones requirements"""
    value = tender.get("milestones")
    if required and tender_created_after(MILESTONES_VALIDATION_FROM):
        if value is None or len(value) < 1:
            raise_operation_error(
                request, ["Tender should contain at least one milestone"], status=422, name="milestones"
            )
    if delivery_financing and tender_created_after(REQUIRED_DELIVERY_AND_FINANCING_MILESTONES_VALIDATION_FROM):
        if value is None or not {TenderMilestoneType.DELIVERY, TenderMilestoneType.FINANCING}.issubset(
            set(x.get("type") for x in value)
        ):
            raise_operation_error(
                request,
                [
                    f"Tender should contain at least one {TenderMilestoneType.DELIVERY} "
                    f"and one {TenderMilestoneType.FINANCING} milestone"
                ],
                status=422,
                name="milestones",
            )


# ================= procedure-specific request validators (former tender/<procedure>/procedure/validation.py) =================


# --- belowThreshold ---


# --- requestForProposal ---

# --- closeFrameworkAgreementSelectionUA ---


# --- closeFrameworkAgreementUA ---


# lot
# --- competitiveDialogue ---


def validate_shortlisted_firms_author(request, tender, obj, obj_name):
    """Compare author key and key from shortlistedFirms"""
    shortlisted_firms = tender["shortlistedFirms"]
    firms_keys = prepare_shortlisted_firms_keys(shortlisted_firms)
    author_key = prepare_shortlisted_firms_author_key(obj)
    if obj.get("questionOf") == "item":  # question can create on item
        if shortlisted_firms[0].get("lots"):
            item_id = author_key.split("_")[-1]
            item = find_item_by_id(tender.get("items", ""), item_id)
            author_key = author_key.replace(author_key.split("_")[-1], item["relatedLot"] if item else "")
        else:
            author_key = "_".join(author_key.split("_")[:-1])
    for firm in firms_keys:
        if author_key in firm:  # if we found legal firm then check another complaint
            break
    else:  # we didn't find legal firm, then return error
        error_message = "Author can't {} {}".format("create" if request.method == "POST" else "patch", obj_name)
        request.errors.add("body", "author", error_message)
        request.errors.status = 403
        raise error_handler(request)


# --- limited (reporting / negotiation / negotiation.quick) ---


# award
