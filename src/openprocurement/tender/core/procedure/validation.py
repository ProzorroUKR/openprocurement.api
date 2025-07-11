import logging
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta
from decimal import ROUND_FLOOR, Decimal
from hashlib import sha512
from typing import Callable

from pyramid.httpexceptions import HTTPError
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.request import Request
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
    FUNDERS,
    GMDN_2019_SCHEME,
    GMDN_2023_SCHEME,
    GMDN_CPV_PREFIXES,
    GUARANTEE_ALLOWED_TENDER_TYPES,
    INN_SCHEME,
    UA_ROAD_CPV_PREFIXES,
    UA_ROAD_SCHEME,
    WORKING_DAYS,
)
from openprocurement.api.constants_env import (
    CONFIDENTIAL_EDRPOU_LIST,
    CONTRACT_OWNER_REQUIRED_FROM,
    CRITERION_REQUIREMENT_STATUSES_FROM,
    ITEMS_UNIT_VALUE_AMOUNT_VALIDATION_FROM,
    RELEASE_2020_04_19,
    RELEASE_ECRITERIA_ARTICLE_17,
    RELEASE_GUARANTEE_CRITERION_FROM,
    TENDER_SIGNER_INFO_REQUIRED_FROM,
)
from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.document import ConfidentialityType
from openprocurement.api.procedure.models.organization import ProcuringEntityKind
from openprocurement.api.procedure.utils import is_item_owner, to_decimal
from openprocurement.api.utils import (
    error_handler,
    is_gmdn_classification,
    is_ua_road_classification,
    raise_operation_error,
)
from openprocurement.api.validation import validate_tender_first_revision_date
from openprocurement.tender.core.constants import (
    AMOUNT_NET_COEF,
    FIRST_STAGE_PROCUREMENT_TYPES,
)
from openprocurement.tender.core.procedure.utils import (
    find_lot,
    get_criterion_requirement,
    get_requirement_obj,
    is_multi_currency_tender,
    tender_created_after,
    tender_created_after_2020_rules,
    tender_created_before,
)
from openprocurement.tender.core.utils import (
    calculate_tender_date,
    calculate_tender_full_date,
)
from openprocurement.tender.pricequotation.constants import PQ

LOGGER = logging.getLogger(__name__)
OPERATIONS = {"POST": "add", "PATCH": "update", "PUT": "update", "DELETE": "delete"}


def validate_item_operation_in_disallowed_tender_statuses(item_name, allowed_statuses):
    """
    Factory sallowed operation in specified statuses
    :param item_name: str
    :param allowed_statuses: list
    :return:
    """

    def validate(request, **_):
        tender = request.validated["tender"]
        if tender["status"] not in allowed_statuses:
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} {item_name} in current ({tender['status']}) tender status",
            )

    return validate


def validate_any_bid_owner(statuses=("active", "unsuccessful")):
    def validator(request, **_):
        tender = request.validated["tender"]
        for bid in tender.get("bids", ""):
            if bid["status"] in statuses and is_item_owner(request, bid):
                return

        raise_operation_error(request, "Forbidden", location="url", name="permission")

    return validator


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


def unless_reviewers(*validations):
    def decorated(request, **_):
        if request.authenticated_role != "aboveThresholdReviewers":
            for validation in validations:
                validation(request)

    return decorated


def validate_any(*validations):
    """
    use case:
    @json_view(
        validators=(
            validate_any(
                validate_item_owner("tender"),
                validate_item_owner("bid"),
            ),
            ...
        ),
        ...
    )
    :param validations:
    :return:
    """

    def decorated(request, **_):
        e = AssertionError("validations list can't be empty")
        errors_on_start = deepcopy(request.errors)
        for validation in validations:
            try:
                validation(request)
            except HTTPError as err:
                e = err
            else:  # on success
                request.errors = errors_on_start
                break
        else:
            raise e

    return decorated


# bids
def validate_bid_operation_period(request, **_):
    tender = request.validated["tender"]
    tender_period = tender.get("tenderPeriod", {})
    if (
        tender_period.get("startDate")
        and get_request_now().isoformat() < tender_period.get("startDate")
        or get_request_now().isoformat() > tender_period.get("endDate", "")  # TODO: may "endDate" be missed ?
    ):
        operation = "added" if request.method == "POST" else "deleted"
        if request.authenticated_role != "Administrator" and request.method in (
            "PUT",
            "PATCH",
        ):
            operation = "updated"
        raise_operation_error(
            request,
            "Bid can be {} only during the tendering period: from ({}) to ({}).".format(
                operation,
                tender_period.get("startDate"),
                tender_period.get("endDate"),
            ),
        )


def validate_bid_operation_in_tendering(request, **_):
    tender_status = request.validated["tender"]["status"]
    if tender_status == "active.tendering":
        raise_operation_error(
            request,
            "Can't view {} in current ({}) tender status".format(
                "bid" if request.matchdict.get("bid_id") else "bids", tender_status
            ),
        )


def validate_bid_operation_not_in_tendering(request, **_):
    status = request.validated["tender"]["status"]
    if status != "active.tendering":
        operation = "add" if request.method == "POST" else "delete"
        if request.authenticated_role != "Administrator" and request.method in (
            "PUT",
            "PATCH",
        ):
            operation = "update"
        raise_operation_error(
            request,
            "Can't {} bid in current ({}) tender status".format(operation, status),
        )


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


def validate_bid_value(tender, value):
    if tender.get("lots"):
        if value:
            raise ValidationError("value should be posted for each lot of bid")
    else:
        tender_value = tender.get("value")
        if not value:
            raise ValidationError("This field is required.")
        config = get_tender()["config"]
        if config.get("valueCurrencyEquality"):
            if tender_value["currency"] != value.currency:
                raise ValidationError("currency of bid should be identical to currency of value of tender")
            if config.get("hasValueRestriction") and to_decimal(tender_value["amount"]) < to_decimal(value.amount):
                raise ValidationError("value of bid should be less than value of tender")
        if tender_value["valueAddedTaxIncluded"] != value.valueAddedTaxIncluded:
            raise ValidationError(
                "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of tender"
            )


def validate_related_lot(tender, related_lot):
    if related_lot not in [lot["id"] for lot in tender.get("lots") or [] if lot]:
        raise ValidationError("relatedLot should be one of lots")


def validate_view_bid_document(request, **_):
    config = get_tender()["config"]
    if config.get("hasPrequalification"):
        forbidden_tender_statuses = ("active.tendering",)
    else:
        forbidden_tender_statuses = ("active.tendering", "active.auction")
    tender_status = request.validated["tender"]["status"]
    if tender_status in forbidden_tender_statuses and not is_item_owner(request, request.validated["bid"]):
        raise_operation_error(
            request,
            "Can't view bid documents in current ({}) tender status".format(tender_status),
        )


def validate_view_bids(request, **_):
    config = get_tender()["config"]
    if config.get("hasPrequalification"):
        forbidden_tender_statuses = ("active.tendering",)
    else:
        forbidden_tender_statuses = ("active.tendering", "active.auction")
    tender_status = request.validated["tender"]["status"]
    if tender_status in forbidden_tender_statuses:
        raise_operation_error(
            request,
            "Can't view {} in current ({}) tender status".format(
                "bid" if request.matchdict.get("bid_id") else "bids", tender_status
            ),
        )


def validate_update_deleted_bid(request, **_):
    if request.validated["bid"]["status"] == "deleted":
        raise_operation_error(request, "Can't update bid in (deleted) status")


def validate_bid_document_operation_period(request, **_):
    tender = request.validated["tender"]
    now = get_request_now().isoformat()
    if tender["status"] == "active.tendering":
        tender_period = tender["tenderPeriod"]
        if tender_period.get("startDate") and now < tender_period["startDate"] or now > tender_period["endDate"]:
            raise_operation_error(
                request,
                "Document can be {} only during the tendering period: from ({}) to ({}).".format(
                    "added" if request.method == "POST" else "updated",
                    tender_period.get("startDate"),
                    tender_period["endDate"],
                ),
            )


# bids req response
def base_validate_operation_ecriteria_objects(request, valid_statuses="", obj_name="tender"):
    validate_tender_first_revision_date(request, validation_date=RELEASE_ECRITERIA_ARTICLE_17)
    current_status = request.validated[obj_name]["status"]
    if current_status not in valid_statuses:
        raise_operation_error(
            request,
            "Can't {} object if {} not in {} statuses".format(request.method.lower(), obj_name, valid_statuses),
        )


def validate_operation_ecriteria_on_tender_status(request, **_):
    valid_statuses = ["draft", "draft.pending", "draft.stage2", "active.tendering"]
    base_validate_operation_ecriteria_objects(request, valid_statuses)


def validate_operation_award_requirement_response(request, **kwargs):
    validate_tender_first_revision_date(request, validation_date=RELEASE_ECRITERIA_ARTICLE_17)
    valid_tender_statuses = ["active.qualification"]
    base_validate_operation_ecriteria_objects(request, valid_tender_statuses)


def validate_view_requirement_responses(request, **_):
    pre_qualification_tenders = [
        "aboveThresholdEU",
        "competitiveDialogueUA",
        "competitiveDialogueEU",
        "competitiveDialogueEU.stage2",
        "esco",
        "closeFrameworkAgreementUA",
    ]

    tender_type = request.validated["tender"]["procurementMethodType"]
    if tender_type in pre_qualification_tenders:
        invalid_tender_statuses = ["active.tendering"]
    else:
        invalid_tender_statuses = ["active.tendering", "active.auction"]

    tender_status = request.validated["tender"]["status"]
    if tender_status in invalid_tender_statuses:
        raise_operation_error(
            request,
            f"Can't view {'bid' if request.matchdict.get('bid_id') else 'bids'} "
            f"in current ({tender_status}) tender status",
        )


# qualification req response
def validate_operation_qualification_requirement_response(request, **_):
    validate_tender_first_revision_date(request, validation_date=RELEASE_ECRITERIA_ARTICLE_17)
    base_validate_operation_ecriteria_objects(request, ["pending"], "qualification")


# bid req response evidence
def validate_operation_ecriteria_objects_evidences(request, **_):
    valid_statuses = ["draft", "draft.pending", "draft.stage2", "active.tendering"]

    tender = request.validated["tender"]
    requirement_id = request.validated["requirement_response"]["requirement"]["id"]
    criterion = get_criterion_requirement(tender, requirement_id)

    if criterion and criterion["source"] == "winner":
        awarded_status = ["active.awarded", "active.qualification"]
        if tender["procurementMethodType"] in ("closeFrameworkAgreementUA",):
            awarded_status.append("active.qualification.stand-still")
        valid_statuses.extend(awarded_status)
        if tender["status"] not in awarded_status:
            raise_operation_error(request, f"available only in {awarded_status} statuses")

        bid_id = request.validated["bid"]["id"]
        active_award = None
        for award in tender.get("awards", ""):
            if award["status"] == "active" and award["bid_id"] == bid_id:
                active_award = award
                break

        if active_award is None:
            raise_operation_error(request, "Winner criteria available only with active award")

        current_contract = None
        for contract in tender.get("contracts", ""):
            if contract.get("awardId") == active_award["id"]:
                current_contract = contract
                break
        if current_contract and current_contract.status == "pending":
            raise_operation_error(request, "forbidden if contract not in status `pending`")

    base_validate_operation_ecriteria_objects(request, valid_statuses)


# for openua, openeu
def unless_allowed_by_qualification_milestone(*validations):
    """
    decorator for 24hours and anomaly low price features to skip some view validator functions
    :param validation: a function runs unless it's disabled by an active qualification milestone
    :return:
    """

    def decorated_validation(request, **_):
        now = get_request_now().isoformat()
        tender = request.validated["tender"]
        bid_id = request.validated["bid"]["id"]
        awards = [q for q in tender.get("awards", "") if q["status"] == "pending" and q["bid_id"] == bid_id]

        # 24 hours
        if "qualifications" in tender:  # for procedures with pre-qualification
            qualifications = [q for q in tender["qualifications"] if q["status"] == "pending" and q["bidID"] == bid_id]
        else:
            qualifications = awards

        for q in qualifications:
            for milestone in q.get("milestones", ""):
                if milestone["code"] == "24h" and milestone["date"] <= now <= milestone["dueDate"]:
                    return  # skipping the validation because of 24 hour milestone

        # low price
        for award in awards:
            for milestone in award.get("milestones", ""):
                if milestone["date"] <= now <= milestone["dueDate"]:
                    if milestone["code"] == "alp":
                        return  # skipping the validation because of low price milestone

        # else
        for validation in validations:
            validation(request)

    return decorated_validation


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


def validate_auction_tender_non_lot(request, **_):
    tender = request.validated["tender"]
    if tender.get("lots"):
        raise_operation_error(
            request,
            [{"participationUrl": ["url should be posted for each lot of bid"]}],
            location="body",
            name="bids",
            status=422,
        )


def validate_active_lot(request, **_):
    tender = request.validated["tender"]
    lot_id = request.matchdict.get("auction_lot_id")
    if not any(lot["status"] == "active" for lot in tender.get("lots", "") if lot["id"] == lot_id):
        raise_operation_error(
            request,
            "Can {} only in active lot status".format(
                "report auction results" if request.method == "POST" else "update auction urls"
            ),
        )


# award
def validate_create_award_not_in_allowed_period(request, **_):
    tender = request.validated["tender"]
    if tender["status"] != "active.qualification":
        raise_operation_error(request, f"Can't create award in current ({tender['status']}) tender status")


def validate_create_award_only_for_active_lot(request, **_):
    tender = request.validated["tender"]
    award = request.validated["data"]
    if any(lot.get("status") != "active" for lot in tender.get("lots", "") if lot["id"] == award.get("lotID")):
        raise_operation_error(request, "Can create award only in active lot status")


def validate_update_award_in_not_allowed_status(request, **_):
    tender = request.validated["tender"]
    if tender["status"] not in ("active.qualification", "active.awarded"):
        raise_operation_error(request, f"Can't update award in current ({tender['status']}) tender status")


def validate_update_award_only_for_active_lots(request, **_):
    tender = request.validated["tender"]
    award = request.validated["award"]
    if any(lot.get("status") != "active" for lot in tender.get("lots", "") if lot.get("id") == award.get("lotID")):
        raise_operation_error(request, "Can update award only in active lot status")


def validate_award_with_lot_cancellation_in_pending(request, **_):
    if not tender_created_after_2020_rules():
        return

    if request.authenticated_role != "tender_owner":
        return

    if request.method == "POST":
        award = request.validated["data"]
    else:
        award = request.validated["award"]
    lot_id = award.get("lotID")
    if not lot_id:
        return

    tender = get_tender()
    accept_lot = all(
        any(complaint.get("status") == "resolved" for complaint in cancellation["complaints"])
        for cancellation in tender.get("cancellations", [])
        if cancellation.get("status") == "unsuccessful"
        and cancellation.get("complaints")
        and cancellation.get("relatedLot") == lot_id
    )
    has_lot_pending_cancellations = any(
        cancellation.get("relatedLot") == lot_id and cancellation.get("status") == "pending"
        for cancellation in tender.get("cancellations", [])
    )
    if has_lot_pending_cancellations or not accept_lot:
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} award with lot that have active cancellation",
        )


def validate_update_award_with_accepted_complaint(request, **_):
    tender = get_tender()
    lot_id = request.validated["award"].get("lotID")
    if any(
        any(c.get("status") == "accepted" for c in i.get("complaints", ""))
        for i in tender.get("awards", "")
        if i.get("lotID") == lot_id
    ):
        raise_operation_error(request, "Can't update award with accepted complaint")


def validate_update_award_status_before_milestone_due_date(request, **_):
    # pylint: disable-next=import-outside-toplevel, cyclic-import
    from openprocurement.tender.core.procedure.models.qualification_milestone import (
        QualificationMilestoneCode,
    )

    award = request.validated["award"]
    sent_status = request.json.get("data", {}).get("status")
    if award.get("status") == "pending" and sent_status != "pending":
        now = get_request_now().isoformat()
        for milestone in award.get("milestones", ""):
            if (
                milestone["code"]
                in (
                    QualificationMilestoneCode.CODE_24_HOURS.value,
                    QualificationMilestoneCode.CODE_LOW_PRICE.value,
                )
                and milestone["date"] <= now <= milestone["dueDate"]
            ):
                raise_operation_error(
                    request,
                    f"Can't change status to '{sent_status}' until milestone.dueDate: {milestone['dueDate']}",
                )


# AWARD DOCUMENTS
def validate_award_document_tender_not_in_allowed_status_base(request, allowed_bot_statuses=("active.awarded",), **_):
    allowed_tender_statuses = ["active.qualification"]
    if request.authenticated_role == "bots":
        allowed_tender_statuses.extend(allowed_bot_statuses)
    status = request.validated["tender"]["status"]
    if status not in allowed_tender_statuses:
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current ({status}) tender status",
        )


def validate_award_document_lot_not_in_allowed_status(request, **_):
    award_lot_id = request.validated["award"].get("lotID")
    if any(
        i.get("status", "active") != "active"
        for i in request.validated["tender"].get("lots", "")
        if i["id"] == award_lot_id
    ):
        raise_operation_error(
            request,
            f"Can {OPERATIONS.get(request.method)} document only in active lot status",
        )


def get_award_document_role(request):
    tender = request.validated["tender"]
    if is_item_owner(request, tender):
        role = "tender_owner"
    else:
        role = request.authenticated_role
    return role


def validate_award_document_author(request, **_):
    doc_author = request.validated["document"].get("author") or "tender_owner"
    role = get_award_document_role(request)
    if doc_author == "bots" and role != "bots":
        # if role != doc_author:   # TODO: unkoment when "author": "brokers" fixed
        raise_operation_error(
            request,
            "Can update document only author",
            location="url",
            name="role",
        )


# TENDER
def validate_tender_status_allows_update(*statuses):
    def validate(request, **_):
        tender_status = get_tender()["status"]
        if tender_status not in statuses:
            raise_operation_error(request, f"Can't update tender in current ({tender_status}) status")

    return validate


def validate_item_quantity(request, **_):
    items = request.validated["data"].get("items", [])
    for item in items:
        if item.get("quantity") is not None and not item["quantity"]:
            if tender_created_after(CRITERION_REQUIREMENT_STATUSES_FROM):
                tender = get_tender()
                related_criteria = any(
                    criterion.get("relatedItem") == item["id"] and requirement.get("status") == "active"
                    for criterion in tender.get("criteria", "")
                    for rg in criterion.get("requirementGroups", "")
                    for requirement in rg.get("requirements", "")
                )
                if related_criteria:
                    raise_operation_error(
                        request,
                        f"Can't set to 0 quantity of {item['id']} item while related criterion has active requirements",
                    )


def validate_tender_guarantee(request, **_):
    if tender_created_before(RELEASE_GUARANTEE_CRITERION_FROM):
        return

    tender = request.validated["tender"]
    data = request.validated["data"]
    new_status = data.get("status")
    if tender["status"] == new_status:
        return

    if new_status not in ("active", "active.tendering"):
        return

    tender_type = tender["procurementMethodType"]
    if tender_type not in GUARANTEE_ALLOWED_TENDER_TYPES:
        return

    if tender.get("lots"):
        related_guarantee_lots = [
            criterion.get("relatedItem")
            for criterion in tender.get("criteria", "")
            if criterion.get("relatesTo") == "lot"
            and criterion.get("classification")
            and criterion["classification"]["id"] == "CRITERION.OTHER.BID.GUARANTEE"
        ]
        for lot in tender["lots"]:
            if lot["id"] in related_guarantee_lots and (not lot.get("guarantee") or lot["guarantee"]["amount"] <= 0):
                raise_operation_error(request, "Should be specified 'guarantee.amount' more than 0 to lot")

    else:
        amount = data["guarantee"]["amount"] if data.get("guarantee") else 0
        needed_criterion = "CRITERION.OTHER.BID.GUARANTEE"
        tender_criteria = [
            criterion["classification"]["id"]
            for criterion in tender.get("criteria", "")
            if criterion.get("classification")
        ]
        if (amount <= 0 and needed_criterion in tender_criteria) or (
            amount > 0 and needed_criterion not in tender_criteria
        ):
            raise_operation_error(
                request,
                "Should be specified {} and 'guarantee.amount' more than 0".format(needed_criterion),
            )


def validate_tender_change_status_with_cancellation_lot_pending(request, **_):
    if not tender_created_after_2020_rules():
        return

    tender = request.validated["tender"]

    if not tender.get("lots"):
        return

    data = request.validated["data"]
    new_status = data.get("status", tender["status"])

    if tender["status"] == new_status:
        return

    accept_lot = all(
        any(j.get("status") == "resolved" for j in i.get("complaints", ""))
        for i in tender.get("cancellations", "")
        if i.get("status") == "unsuccessful" and i.get("complaints") and i.get("relatedLot")
    )
    if (
        any(i.get("relatedLot") and i.get("status") == "pending" for i in tender.get("cancellations", ""))
        or not accept_lot
    ):
        raise_operation_error(
            request,
            "Can't update tender with pending cancellation in one of exists lot",
        )


# tender documents
def validate_document_operation_in_allowed_tender_statuses(allowed_statuses):
    """
    Factory allowed operation in specified statuses
    :param allowed_statuses: list
    :return:
    """

    def validate(request, **_):
        valid_statuses = list(allowed_statuses)

        if request.authenticated_role == "auction":
            valid_statuses = [
                "active.auction",
                "active.qualification",
            ]
        else:
            data = request.validated["data"]
            documents = data if isinstance(data, list) else [data]

            # Check if all documents are evaluation reports (sign docs)
            if all(doc.get("documentType") == "evaluationReports" for doc in documents):
                # If it's only sign docs, then we can allow operation in pre-qualification status
                valid_statuses.append("active.pre-qualification")

        tender_status = request.validated["tender"]["status"]
        if tender_status not in valid_statuses:
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} document in current ({tender_status}) tender status",
            )

    return validate


validate_tender_document_operation_in_allowed_tender_statuses = validate_document_operation_in_allowed_tender_statuses(
    (
        "draft",
        "draft.stage2",  # competitive dialogue
        "active.enquiries",
        "active.tendering",
    )
)


def get_tender_document_role(request):
    tender = request.validated["tender"]
    if is_item_owner(request, tender):
        role = "tender_owner"
    else:
        role = request.authenticated_role
    return role


def validate_tender_document_update_not_by_author_or_tender_owner(request, **_):
    document = request.validated["document"]
    role = get_tender_document_role(request)
    if role != (document.get("author") or "tender_owner"):
        request.errors.add("url", "role", "Can update document only author")
        request.errors.status = 403
        raise error_handler(request)


# QUALIFICATION
def validate_qualification_update_not_in_pre_qualification(request, **_):
    status = request.validated["tender"]["status"]
    if status not in ["active.pre-qualification"]:
        raise_operation_error(request, f"Can't update qualification in current ({status}) tender status")


def validate_cancelled_qualification_update(request, **_):
    status = request.validated["qualification"]["status"]
    if status == "cancelled":
        raise_operation_error(
            request,
            "Can't update qualification in current cancelled qualification status",
        )


def validate_update_qualification_only_for_active_lots(request, **_):
    tender = request.validated["tender"]
    qualification = request.validated["qualification"]
    if any(
        lot.get("status") != "active" for lot in tender.get("lots", "") if lot.get("id") == qualification.get("lotID")
    ):
        raise_operation_error(request, "Can update qualification only in active lot status")


def validate_update_status_before_milestone_due_date(request, **_):
    # pylint: disable-next=import-outside-toplevel, cyclic-import
    from openprocurement.tender.core.procedure.models.qualification_milestone import (
        QualificationMilestoneCode,
    )

    qualification = request.validated["qualification"]
    sent_status = request.validated["data"].get("status")
    if qualification.get("status") == "pending" and qualification.get("status") != sent_status:
        now = get_request_now().isoformat()
        for milestone in qualification.get("milestones", []):
            if (
                milestone["code"]
                in (
                    QualificationMilestoneCode.CODE_24_HOURS.value,
                    QualificationMilestoneCode.CODE_LOW_PRICE.value,
                )
                and milestone["date"] <= now <= milestone["dueDate"]
            ):
                raise_operation_error(
                    request,
                    f"Can't change status to '{sent_status}' until milestone.dueDate: {milestone['dueDate']}",
                )


# QUALIFICATION DOCUMENT
def get_qualification_document_role(request):
    tender = request.validated["tender"]
    if is_item_owner(request, tender):
        role = "tender_owner"
    else:
        role = request.authenticated_role
    return role


def validate_qualification_update_with_cancellation_lot_pending(request, **kwargs):
    if not tender_created_after_2020_rules():
        return

    qualification = request.validated["qualification"]
    lot_id = qualification.get("lotID")

    if not lot_id:
        return

    tender = request.validated["tender"]
    accept_lot = all(
        [
            any(j["status"] == "resolved" for j in i["complaints"])
            for i in tender.get("cancellations", [])
            if i["status"] == "unsuccessful" and getattr(i, "complaints", None) and i["relatedLot"] == lot_id
        ]
    )

    if request.authenticated_role == "tender_owner" and (
        any(
            i["status"] == "pending" and i.get("relatedLot") and i["relatedLot"] == lot_id
            for i in tender.get("cancellations", "")
        )
        or not accept_lot
    ):
        raise_operation_error(
            request,
            "Can't update qualification with pending cancellation lot",
        )


def validate_qualification_document_operation_not_in_allowed_status(request, **_):
    if request.validated["tender"]["status"] != "active.pre-qualification":
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current ({request.validated['tender']['status']}) tender status",
        )


def validate_qualification_document_operation_not_in_pending(request, **_):
    qualification = request.validated["qualification"]
    if qualification["status"] != "pending":
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current qualification status",
        )


# lot


validate_lot_operation_in_disallowed_tender_statuses = validate_item_operation_in_disallowed_tender_statuses(
    "lot", ("active.tendering", "draft", "draft.stage2")
)


def validate_operation_with_lot_cancellation_in_pending(type_name: str) -> Callable:
    def validation(request: Request, **_) -> None:
        if not tender_created_after_2020_rules():
            return

        fields_names = {
            "lot": "id",
            "award": "lotID",
            "qualification": "lotID",
            "complaint": "relatedLot",
            "question": "relatedItem",
        }

        tender = request.validated["tender"]

        field = fields_names.get(type_name)
        if not field:
            return

        o = request.validated.get(type_name)
        lot_id = getattr(o, field, None)

        if not lot_id:
            return

        msg = "Can't {} {} with lot that have active cancellation"
        if type_name == "lot":
            msg = "Can't {} lot that have active cancellation"

        accept_lot = all(
            [
                any(j["status"] == "resolved" for j in i["complaints"])
                for i in tender.get("cancellations", [])
                if i["status"] == "unsuccessful" and getattr(i, "complaints", None) and i["relatedLot"] == lot_id
            ]
        )

        if request.authenticated_role == "tender_owner" and (
            any(
                [
                    i
                    for i in tender.get("cancellations", [])
                    if i["relatedLot"] and i["status"] == "pending" and i["relatedLot"] == lot_id
                ]
            )
            or not accept_lot
        ):
            raise_operation_error(
                request,
                msg.format(OPERATIONS.get(request.method), type_name),
            )

    return validation


def _validate_related_criterion(request: Request, relatedItem_id: str, action="cancel", relatedItem="lot") -> None:
    if tender_created_before(CRITERION_REQUIREMENT_STATUSES_FROM):
        return
    tender = request.validated["tender"]
    if tender.get("criteria"):
        related_criteria = [
            criterion
            for criterion in tender["criteria"]
            for rg in criterion.get("requirementGroups", "")
            for requirement in rg.get("requirements", "")
            if criterion.get("relatedItem", "") == relatedItem_id and requirement["status"] == "active"
        ]
        if related_criteria:
            raise_operation_error(
                request,
                "Can't {} {} {} while related criterion has active requirements".format(
                    action, relatedItem_id, relatedItem
                ),
            )


def _validate_related_object(request: Request, collection_name: str, lot_id: str) -> None:
    tender = request.validated["tender"]
    exist_related_obj = any(i.get("relatedLot", "") == lot_id for i in tender.get(collection_name, ""))

    if exist_related_obj:
        raise_operation_error(request, f"Cannot delete lot with related {collection_name}", status=422)


def validate_delete_lot_related_object(request: Request, **_) -> None:
    # We have some realization of that's validations in tender
    # This logic is duplicated
    lot_id = request.validated["lot"]["id"]
    _validate_related_criterion(request, lot_id, action="delete")
    _validate_related_object(request, "cancellations", lot_id)
    _validate_related_object(request, "milestones", lot_id)
    _validate_related_object(request, "items", lot_id)


def validate_24h_milestone_released(request, **kwargs):
    validate_tender_first_revision_date(request, validation_date=RELEASE_2020_04_19)


def is_positive_float(value):
    if value <= 0:
        raise ValidationError("Float value should be greater than 0.")


def validate_bid_document_operation_in_award_status(request, **_):
    tender = request.validated["tender"]
    bid = request.validated["bid"]

    allowed_award_statuses = ("active",)

    if tender["status"] in ("active.qualification", "active.awarded") and not any(
        award["status"] in allowed_award_statuses and award["bid_id"] == bid["id"] for award in tender.get("awards", "")
    ):
        raise_operation_error(
            request,
            "Can't {} document because award of bid is not in one of statuses {}".format(
                OPERATIONS.get(request.method), allowed_award_statuses
            ),
        )


def validate_bid_document_in_tender_status_base(request, allowed_statuses):
    """
    active.tendering - tendering docs
    active.qualification - multi-lot procedure may be in this status despite the active award
    active.awarded - qualification docs that should be posted into award (another temp solution)
    """
    tender = request.validated["tender"]
    status = tender["status"]
    if status not in allowed_statuses:
        operation = OPERATIONS.get(request.method)
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(operation, status),
        )


def validate_bid_document_in_tender_status(request, **_):
    """
    active.tendering - tendering docs
    active.awarded - qualification docs that should be posted into award (another temp solution)
    """
    tender = request.validated["tender"]
    allowed_statuses = (
        "active.tendering",
        "active.qualification",
        "active.awarded",
    )

    if tender["procurementMethodType"] in ("closeFrameworkAgreementUA",):
        allowed_statuses += ("active.qualification.stand-still",)

    validate_bid_document_in_tender_status_base(request, allowed_statuses)


def validate_download_tender_document(request, **_):
    if request.params.get("download"):
        document = request.validated["document"]
        if (
            document.get("confidentiality", "") == ConfidentialityType.BUYER_ONLY
            and request.authenticated_role not in ("aboveThresholdReviewers", "sas")
            and not ("bid" in request.validated and is_item_owner(request, request.validated["bid"]))
            and not is_item_owner(request, request.validated["tender"])
        ):
            raise_operation_error(request, "Document download forbidden.")


def validate_update_bid_document_confidentiality(request, **_):
    tender_status = request.validated["tender"]["status"]
    if tender_status != "active.tendering" and "confidentiality" in request.validated.get("data", {}):
        document = request.validated["document"]
        if document.get("confidentiality", "public") != request.validated["data"]["confidentiality"]:
            raise_operation_error(
                request,
                "Can't update document confidentiality in current ({}) tender status".format(tender_status),
            )


def validate_bid_document_operation_in_bid_status(request, **_):
    bid = request.validated["bid"]
    if bid["status"] in ("unsuccessful", "deleted"):
        raise_operation_error(
            request,
            "Can't {} document at '{}' bid status".format(OPERATIONS.get(request.method), bid["status"]),
        )


def validate_view_bid_documents_allowed_in_bid_status(request, **_):
    bid_status = request.validated["bid"]["status"]
    if bid_status in ("invalid", "deleted") and not is_item_owner(request, request.validated["bid"]):
        raise_operation_error(request, f"Can't view bid documents in current ({bid_status}) bid status")


def validate_view_financial_bid_documents_allowed_in_tender_status(request, **_):
    tender_status = request.validated["tender"]["status"]
    forbidden_tender_statuses = (
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
        "active.auction",
    )
    if tender_status in forbidden_tender_statuses and not is_item_owner(request, request.validated["bid"]):
        raise_operation_error(
            request,
            f"Can't view bid documents in current ({tender_status}) tender status",
        )


def validate_view_financial_bid_documents_allowed_in_bid_status(request, **_):
    bid_status = request.validated["bid"]["status"]
    forbidden_bid_statuses = (
        "invalid",
        "deleted",
        "invalid.pre-qualification",
        "unsuccessful",
    )
    if bid_status in forbidden_bid_statuses and not is_item_owner(request, request.validated["bid"]):
        raise_operation_error(request, f"Can't view bid documents in current ({bid_status}) bid status")


def validate_tender_status_for_put_action_period(request, **_):
    tender_status = request.validated["tender"]["status"]
    if tender_status not in (
        "active.auction",
        "active.pre-qualification",
        "active.tendering",
    ):
        raise_operation_error(
            request,
            f"Can't update auctionPeriod in current ({tender_status}) tender status",
        )


def validate_auction_period_start_date(request, **kwargs):
    tender = request.validated["tender"]
    data = request.validated["data"]
    start_date = data.get("startDate", {})
    if start_date:
        if (get_request_now() + timedelta(seconds=3600)).isoformat() > start_date:
            raise_operation_error(
                request,
                "startDate should be no earlier than an hour later",
            )
        if tender.get("auctionPeriod", {}).get("shouldStartAfter"):
            if start_date < tender["auctionPeriod"]["shouldStartAfter"]:
                raise_operation_error(
                    request,
                    "startDate should be after shouldStartAfter",
                )


def validate_lot_status_active(request, **_):
    tender = request.validated["tender"]
    lot_id = request.matchdict.get("lot_id")
    if not any(lot["status"] == "active" for lot in tender.get("lots", "") if lot["id"] == lot_id):
        raise_operation_error(
            request,
            "Can update auction urls only in active lot status",
        )


# Plans
def validate_procurement_kind_is_central(request, **kwargs):
    if request.validated["tender"]["procuringEntity"]["kind"] != ProcuringEntityKind.CENTRAL:
        raise raise_operation_error(
            request, "Only allowed for procurementEntity.kind = '{}'".format(ProcuringEntityKind.CENTRAL)
        )


def validate_tender_in_draft(request, **kwargs):
    if request.validated["tender"]["status"] not in ("draft", "draft.stage2"):
        raise raise_operation_error(request, "Only allowed in draft tender status")


def validate_procurement_type_of_first_stage(request, **kwargs):
    tender = request.validated["tender"]
    if tender["procurementMethodType"] not in FIRST_STAGE_PROCUREMENT_TYPES:
        request.errors.add(
            "body",
            "procurementMethodType",
            "Should be one of the first stage values: {}".format(FIRST_STAGE_PROCUREMENT_TYPES),
        )
        request.errors.status = 422
        raise error_handler(request)


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


def validate_tender_period_start_date(data, period, working_days=False, calendar=WORKING_DAYS):
    min_allowed_date = calculate_tender_date(
        get_request_now(),
        -timedelta(minutes=10),
        tender=None,
        working_days=working_days,
        calendar=calendar,
    )
    if min_allowed_date >= period.startDate:
        raise ValidationError("tenderPeriod.startDate should be in greater than current date")


def validate_tender_period_duration(data, period, duration, working_days=False, calendar=WORKING_DAYS):
    tender_period_end_date = calculate_tender_full_date(
        period.startDate,
        duration,
        tender=data,
        working_days=working_days,
        calendar=calendar,
    )
    if tender_period_end_date > period.endDate:
        raise ValidationError(
            "tenderPeriod must be at least {duration.days} full {type} days long".format(
                duration=duration, type="business" if working_days else "calendar"
            )
        )


def validate_funders_unique(funders, *args):
    if funders:
        ids = [(i.identifier.scheme, i.identifier.id) for i in funders if i.identifier]
        if len(ids) > len(set(ids)):
            raise ValidationError("Funders' identifier should be unique")


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


def validate_items_unit_amount(items_unit_value_amount, data, obj_name="contract"):
    if items_unit_value_amount and data.get("value") and not is_multi_currency_tender():
        sum_items_unit = sum(items_unit_value_amount)
        calculated_value = sum_items_unit.quantize(Decimal("1E-2"), rounding=ROUND_FLOOR)
        obj_value = to_decimal(data["value"]["amount"])

        # For PQ from particular date it is required that:
        #  - sum of all items.unit.value.amount should be equal obj value if VAT is not included in obj (without coins)
        #  - sum of items.unit.value.amount < obj value < (sum of items.unit.value.amount * 1.2 ) if VAT is included in obj
        if (
            tender_created_after(ITEMS_UNIT_VALUE_AMOUNT_VALIDATION_FROM)
            and get_tender().get("procurementMethodType") == PQ
        ):
            tax_included = data["value"]["valueAddedTaxIncluded"]
            if tax_included:
                # get amountNet from obj.value if it is set or count this -20% net amount
                obj_amount_net = data["value"].get("amountNet")
                if obj_amount_net is None:
                    obj_amount_net = (obj_value / AMOUNT_NET_COEF).quantize(Decimal("1E-2"), rounding=ROUND_FLOOR)
                # we ignore coins for this validation, that's why int() was used
                if calculated_value <= 0 or not (int(obj_amount_net) <= int(calculated_value) <= int(obj_value)):
                    raise_operation_error(
                        get_request(),
                        f"Total amount of unit values must be no more than {obj_name}.value.amount and no less than net {obj_name} amount",
                        name="items",
                        status=422,
                    )
            elif int(obj_value) != int(calculated_value):  # ignore coins
                raise_operation_error(
                    get_request(),
                    f"Total amount of unit values should be equal {obj_name}.value.amount if VAT is not included in {obj_name}",
                    name="items",
                    status=422,
                )
        elif calculated_value > obj_value:
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


def validate_req_response_values(response):
    requirement, *_ = get_requirement_obj(response["requirement"]["id"])
    if requirement:
        if requirement.get("expectedValues") is not None and response.get("value") is not None:
            raise_operation_error(
                get_request(),
                f"only 'values' allowed in response for requirement {requirement['id']}",
                name="requirementResponses",
                status=422,
            )
        elif requirement.get("expectedValues") is None and response.get("values") is not None:
            raise_operation_error(
                get_request(),
                f"only 'value' allowed in response for requirement {requirement['id']}",
                name="requirementResponses",
                status=422,
            )


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


def validate_signer_info_container(request, tender, container, container_name):
    if isinstance(container, list):
        for index, item in enumerate(container):
            validate_signer_info(request, tender, item, container_name, index)
    else:
        validate_signer_info(request, tender, container, container_name)


def validate_signer_info(request, tender, organization, field_name, field_index=None) -> None:
    signer_info = organization.get("signerInfo")
    contract_owner = organization.get("contract_owner")
    contract_template_name = tender.get("contractTemplateName")
    field_path = f"{field_name}.{field_index}" if field_index is not None else field_name
    if tender_created_after(TENDER_SIGNER_INFO_REQUIRED_FROM) and contract_template_name and not signer_info:
        raise_operation_error(
            request,
            {"signerInfo": BaseType.MESSAGES["required"]},
            name=field_path,
            status=422,
        )
    if contract_owner is not None:
        if not contract_template_name or not signer_info:
            raise_operation_error(
                request,
                {"contract_owner": "could be set only along with signerInfo and contractTemplateName"},
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
    elif tender_created_after(CONTRACT_OWNER_REQUIRED_FROM) and contract_template_name and signer_info:
        raise_operation_error(
            request,
            {"contract_owner": BaseType.MESSAGES["required"]},
            name=field_path,
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
