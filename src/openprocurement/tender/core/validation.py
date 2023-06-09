# -*- coding: utf-8 -*-
from collections import defaultdict

from math import floor, ceil
from decimal import Decimal, ROUND_UP, ROUND_FLOOR

from schematics.types import BaseType
from schematics.types.compound import PolyModelType


from openprocurement.api.validation import (
    validate_data,
    validate_json_data,
    _validate_accreditation_level,
    _validate_accreditation_level_mode,
    OPERATIONS,
)
from openprocurement.api.constants import (
    WORKING_DAYS,
    UA_ROAD_SCHEME,
    UA_ROAD_CPV_PREFIXES,
    GMDN_2019_SCHEME,
    GMDN_2023_SCHEME,
    ATC_SCHEME,
    INN_SCHEME,
    GMDN_CPV_PREFIXES,
    RELEASE_2020_04_19,
    MINIMAL_STEP_VALIDATION_FROM,
    MINIMAL_STEP_VALIDATION_PRESCISSION,
    MINIMAL_STEP_VALIDATION_LOWER_LIMIT,
    MINIMAL_STEP_VALIDATION_UPPER_LIMIT,
)
from openprocurement.api.utils import (
    get_now,
    is_ua_road_classification,
    is_gmdn_classification,
    to_decimal,
    update_logging_context,
    error_handler,
    raise_operation_error,
    handle_data_exceptions,
    get_first_revision_date,
    get_root,
)
from openprocurement.tender.core.constants import AMOUNT_NET_COEF, FIRST_STAGE_PROCUREMENT_TYPES
from openprocurement.tender.core.utils import (
    calculate_tender_business_date,
    requested_fields_changes,
)
from schematics.exceptions import ValidationError
from schematics.types import DecimalType, StringType, IntType, BooleanType, DateTimeType
from openprocurement.tender.pricequotation.constants import PQ


def validate_complaint_data(request, **kwargs):
    update_logging_context(request, {"complaint_id": "__new__"})
    validate_complaint_accreditation_level(request)
    if "cancellation" in request.validated:
        model = type(request.validated["cancellation"]).complaints.model_class
        return validate_data(request, model)
    elif isinstance(type(request.tender).complaints.field, PolyModelType):
        data = validate_json_data(request)
        model = type(request.tender).complaints.field.find_model(data)
        return validate_data(request, model, data=data)
    else:
        model = type(request.tender).complaints.model_class
        return validate_data(request, model)


def validate_complaint_accreditation_level(request, **kwargs):
    tender = request.validated["tender"]
    mode = tender.get("mode", None)
    _validate_accreditation_level(request, tender.edit_accreditations, "complaint", "creation")
    _validate_accreditation_level_mode(request, mode, "complaint", "creation")


def validate_patch_complaint_data(request, **kwargs):
    if "cancellation" in request.validated:
        model = type(request.validated["cancellation"]).complaints.model_class
    else:
        model = type(request.context)
    return validate_data(request, model, True)


# Cancellation complaint
def validate_cancellation_complaint(request, **kwargs):
    old_rules = get_first_revision_date(request.tender, default=get_now()) < RELEASE_2020_04_19
    tender = request.validated["tender"]
    without_complaints = ["belowThreshold", "reporting", "closeFrameworkAgreementSelectionUA"]
    if old_rules or tender.procurementMethodType in without_complaints:
        raise_operation_error(request, "Not Found", status=404)


def validate_cancellation_complaint_add_only_in_pending(request, **kwargs):

    cancellation = request.validated["cancellation"]
    complaint_period = cancellation.complaintPeriod
    if cancellation.status != "pending":
        raise_operation_error(
            request,
            "Complaint can be add only in pending status of cancellation",
            status=422,
        )

    is_complaint_period = (
        complaint_period.startDate <= get_now() <= complaint_period.endDate
        if complaint_period
        else False
    )
    if cancellation.status == "pending" and not is_complaint_period:
        raise_operation_error(
            request,
            "Complaint can't be add after finish of complaint period",
            status=422,
        )



def validate_cancellation_complaint_resolved(request, **kwargs):
    cancellation = request.validated["cancellation"]
    complaint = request.validated["data"]
    if complaint.get("tendererAction") and cancellation.status != "unsuccessful":
        raise_operation_error(
            request,
            "Complaint can't have tendererAction only if cancellation not in unsuccessful status",
            status=422,
        )


def validate_relatedlot(tender, relatedLot):
    if relatedLot not in [lot.id for lot in tender.lots if lot]:
        raise ValidationError("relatedLot should be one of lots")


def validate_lotvalue_value(tender, relatedLot, value):
    if not value and not relatedLot:
        return
    lot = next((lot for lot in tender.lots if lot and lot.id == relatedLot), None)
    if not lot:
        return
    if lot.value.amount < value.amount:
        raise ValidationError("value of bid should be less than value of lot")
    if lot.get("value").currency != value.currency:
        raise ValidationError("currency of bid should be identical to currency of value of lot")
    if lot.get("value").valueAddedTaxIncluded != value.valueAddedTaxIncluded:
        raise ValidationError(
            "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot"
        )


def validate_bid_value(tender, value):
    if tender.lots:
        if value:
            raise ValidationError("value should be posted for each lot of bid")
    else:
        if not value:
            raise ValidationError("This field is required.")
        if tender.value.amount < value.amount:
            raise ValidationError("value of bid should be less than value of tender")
        if tender.get("value").currency != value.currency:
            raise ValidationError("currency of bid should be identical to currency of value of tender")
        if tender.get("value").valueAddedTaxIncluded != value.valueAddedTaxIncluded:
            raise ValidationError(
                "valueAddedTaxIncluded of bid should be identical " "to valueAddedTaxIncluded of value of tender"
            )


def validate_minimalstep(data, value):
    if value and value.amount is not None and data.get("value"):
        if data.get("value").amount < value.amount:
            raise ValidationError("value should be less than value of tender")
        if data.get("value").currency != value.currency:
            raise ValidationError("currency should be identical to currency of value of tender")
        if data.get("value").valueAddedTaxIncluded != value.valueAddedTaxIncluded:
            raise ValidationError(
                "valueAddedTaxIncluded should be identical " "to valueAddedTaxIncluded of value of tender"
            )
        if not data.get("lots"):
            validate_minimalstep_limits(data, value, is_tender=True)


def validate_minimalstep_limits(data, value, is_tender=False):
    if value and value.amount is not None and data.get("value"):
        tender = data if is_tender else get_root(data["__parent__"])
        tender_created = get_first_revision_date(tender, default=get_now())
        if tender_created > MINIMAL_STEP_VALIDATION_FROM:
            precision_multiplier = 10**MINIMAL_STEP_VALIDATION_PRESCISSION
            lower_minimalstep = (floor(float(data.get("value").amount)
                                       * MINIMAL_STEP_VALIDATION_LOWER_LIMIT * precision_multiplier)
                                 / precision_multiplier)
            higher_minimalstep = (ceil(float(data.get("value").amount)
                                       * MINIMAL_STEP_VALIDATION_UPPER_LIMIT * precision_multiplier)
                                  / precision_multiplier)
            if higher_minimalstep < value.amount or value.amount < lower_minimalstep:
                raise ValidationError(
                    "minimalstep must be between 0.5% and 3% of value (with 2 digits precision).")


def validate_tender_period_duration(data, period, duration, working_days=False, calendar=WORKING_DAYS):
    tender_period_end_date = calculate_tender_business_date(
        period.startDate, duration, data,
        working_days=working_days,
        calendar=calendar
    )
    if tender_period_end_date > period.endDate:
        raise ValidationError("tenderPeriod must be at least {duration.days} full {type} days long".format(
            duration=duration,
            type="business" if working_days else "calendar"
        ))


def validate_absence_of_pending_accepted_satisfied_complaints(request, cancellation=None, **kwargs):
    """
    Disallow cancellation of tenders and lots that have any complaints in affected statuses
    """
    tender = request.validated["tender"]
    tender_creation_date = get_first_revision_date(tender, default=get_now())
    if tender_creation_date < RELEASE_2020_04_19:
        return

    if not cancellation:
        cancellation = request.validated["cancellation"]
    cancellation_lot = cancellation.get("relatedLot")

    def validate_complaint(complaint, complaint_lot, item_name):
        """
        raise error if it's:
         - canceling tender that has a complaint (not cancellation_lot)
         - canceling tender that has a lot complaint (not cancellation_lot)
         - canceling lot that has a lot complaint (cancellation_lot == complaint_lot)
         - canceling lot if there is a non-lot complaint (not complaint_lot)
        AND complaint.status is in ("pending", "accepted", "satisfied")
        """
        if not cancellation_lot or not complaint_lot or cancellation_lot == complaint_lot:
            if complaint.get("status") in ("pending", "accepted", "satisfied"):
                raise_operation_error(
                    request,
                    "Can't perform operation for there is {} complaint in {} status".format(
                        item_name, complaint.get("status"))
                )

    for c in tender.get("complaints", ""):
        validate_complaint(c, c.get("relatedLot"), "a tender")

    for qualification in tender.get("qualifications", ""):
        for c in qualification.get("complaints", ""):
            validate_complaint(c, qualification.get("lotID"), "a qualification")

    for award in tender.get("awards", ""):
        for c in award.get("complaints", ""):
            validate_complaint(c, award.get("lotID"), "an award")



# complaints
def validate_complaint_operation_not_in_active_tendering(request, **kwargs):
    tender = request.validated["tender"]
    if tender.status != "active.tendering":
        raise_operation_error(
            request,
            "Can't {} complaint in current ({}) tender status".format(OPERATIONS.get(request.method), tender.status),
        )


def validate_complaint_update_with_cancellation_lot_pending(request, **kwargs):
    tender = request.validated["tender"]
    tender_created = get_first_revision_date(tender, default=get_now())
    complaint = request.validated["complaint"]

    if tender_created < RELEASE_2020_04_19 or not complaint.relatedLot:
        return

    accept_lot = all([
        any([j.status == "resolved" for j in i.complaints])
        for i in tender.cancellations
        if i.status == "unsuccessful" and getattr(i, "complaints", None) and i.relatedLot == complaint.relatedLot
    ])

    if (
        request.authenticated_role == "tender_owner"
        and (
            any([
                i for i in tender.cancellations
                if i.relatedLot and i.status == "pending" and i.relatedLot == complaint.relatedLot])
            or not accept_lot
        )
    ):
        raise_operation_error(
            request,
            "Can't update complaint with pending cancellation lot".format(OPERATIONS.get(request.method)),
        )


def validate_submit_complaint_time(request, **kwargs):
    complaint_submit_time = request.content_configurator.tender_complaint_submit_time
    tender = request.validated["tender"]
    if get_now() > tender.complaintPeriod.endDate:
        raise_operation_error(
            request,
            "Can submit complaint not later than {duration.days} "
            "full calendar days before tenderPeriod ends".format(
                duration=complaint_submit_time
            ),
        )


def validate_update_claim_time(request, **kwargs):
    tender = request.validated["tender"]
    if tender.enquiryPeriod.clarificationsUntil and get_now() > tender.enquiryPeriod.clarificationsUntil:
        raise_operation_error(request, "Can update claim only before enquiryPeriod.clarificationsUntil")


# complaints document
def validate_status_and_role_for_complaint_document_operation(request, **kwargs):
    roles = request.content_configurator.allowed_statuses_for_complaint_operations_for_roles
    if request.validated["complaint"].status not in roles.get(request.authenticated_role, []):
        raise_operation_error(
            request,
            "Can't {} document in current ({}) complaint status".format(
                OPERATIONS.get(request.method), request.validated["complaint"].status
            ),
        )


def validate_complaint_document_update_not_by_author(request, **kwargs):
    if request.authenticated_role != request.context.author:
        request.errors.add("url", "role", "Can update document only author")
        request.errors.status = 403
        raise error_handler(request)


# awards
def validate_update_award_with_cancellation_lot_pending(request, **kwargs):
    tender = request.validated["tender"]
    tender_created = get_first_revision_date(tender, default=get_now())

    award = request.validated["award"]

    if tender_created < RELEASE_2020_04_19 or not award.lotID:
        return

    accept_lot = all([
        any([j.status == "resolved" for j in i.complaints])
        for i in tender.cancellations
        if i.status == "unsuccessful" and getattr(i, "complaints", None) and i.relatedLot == award.lotID
    ])

    if any([
        i for i in tender.cancellations
        if i.relatedLot and i.status == "pending" and i.relatedLot == award.lotID
    ]) or not accept_lot:
        raise_operation_error(request, "Can't update award with pending cancellation lot")


# award complaint
def validate_award_complaint_operation_not_in_allowed_status(request, **kwargs):
    tender = request.validated["tender"]
    if tender.status not in ["active.qualification", "active.awarded"]:
        raise_operation_error(
            request,
            "Can't {} complaint in current ({}) tender status".format(OPERATIONS.get(request.method), tender.status),
        )


def validate_award_complaint_add_only_for_active_lots(request, **kwargs):
    tender = request.validated["tender"]
    if any([i.status != "active" for i in tender.lots if i.id == request.context.lotID]):
        raise_operation_error(request, "Can add complaint only in active lot status")


def validate_award_complaint_update_only_for_active_lots(request, **kwargs):
    tender = request.validated["tender"]
    if any([i.status != "active" for i in tender.lots if i.id == request.validated["award"].lotID]):
        raise_operation_error(request, "Can update complaint only in active lot status")


def validate_add_complaint_with_tender_cancellation_in_pending(request, **kwargs):
    tender = request.validated["tender"]
    tender_created = get_first_revision_date(tender, default=get_now())

    if tender_created < RELEASE_2020_04_19:
        return

    if any([i for i in tender.cancellations if i.status == "pending" and not i.relatedLot]):
        raise_operation_error(request, "Can't add complaint if tender have cancellation in pending status")


def validate_add_complaint_with_lot_cancellation_in_pending(type_name):
    type_name = type_name.lower()

    def validation(request, **kwargs):
        fields_names = {
            "lot": "id",
            "award": "lotID",
            "qualification": "lotID",
            "complaint": "relatedLot",
        }
        tender = request.validated["tender"]
        tender_created = get_first_revision_date(tender, default=get_now())

        field = fields_names.get(type_name)
        o = request.validated.get(type_name)
        lot_id = getattr(o, field, None)

        if tender_created < RELEASE_2020_04_19 or not lot_id:
            return

        if any([
            i for i in tender.cancellations
            if i.relatedLot and i.status == "pending" and i.relatedLot == lot_id
        ]):
            raise_operation_error(
                request,
                "Can't add complaint to {} with 'pending' lot cancellation".format(type_name),
            )

    return validation


def validate_operation_with_lot_cancellation_in_pending(type_name):
    def validation(request, **kwargs):
        fields_names = {
            "lot": "id",
            "award": "lotID",
            "qualification": "lotID",
            "complaint": "relatedLot",
            "question": "relatedItem"
        }

        tender = request.validated["tender"]
        tender_created = get_first_revision_date(tender, default=get_now())

        field = fields_names.get(type_name)
        o = request.validated.get(type_name)
        lot_id = getattr(o, field, None)

        if tender_created < RELEASE_2020_04_19 or not lot_id:
            return

        msg = "Can't {} {} with lot that have active cancellation"
        if type_name == "lot":
            msg = "Can't {} lot that have active cancellation"

        accept_lot = all([
            any([j.status == "resolved" for j in i.complaints])
            for i in tender.cancellations
            if i.status == "unsuccessful" and getattr(i, "complaints", None) and i.relatedLot == lot_id
        ])

        if (
            request.authenticated_role == "tender_owner"
            and (
                any([
                    i for i in tender.cancellations
                    if i.relatedLot and i.status == "pending" and i.relatedLot == lot_id])
                or not accept_lot
            )
        ):
            raise_operation_error(
                request,
                msg.format(OPERATIONS.get(request.method), type_name),
            )
    return validation


def validate_add_complaint_not_in_complaint_period(request, **kwargs):
    period = request.context.complaintPeriod
    award = request.context
    if not (award.status in ["active", "unsuccessful"]
            and period
            and period.startDate <= get_now() < period.endDate):
        raise_operation_error(request, "Can add complaint only in complaintPeriod")


def validate_update_cancellation_complaint_not_in_allowed_complaint_status(request, **kwargs):
    if request.context.status not in ["draft", "pending", "accepted", "satisfied", "stopping"]:
        raise_operation_error(request, "Can't update complaint in current ({}) status".format(request.context.status))


def validate_update_complaint_not_in_allowed_complaint_status(request, **kwargs):
    if request.context.status not in ["draft", "pending", "accepted", "satisfied", "stopping"]:
        raise_operation_error(request, "Can't update complaint in current ({}) status".format(request.context.status))


def validate_update_complaint_not_in_allowed_claim_status(request, **kwargs):
    if request.context.status not in ["draft", "claim", "answered"]:
        raise_operation_error(request, "Can't update complaint in current ({}) status".format(request.context.status))


# award complaint document
def validate_award_complaint_document_operation_not_in_allowed_status(request, **kwargs):
    if request.validated["tender_status"] not in ["active.qualification", "active.awarded"]:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


def validate_award_complaint_document_operation_only_for_active_lots(request, **kwargs):
    if any(
        [i.status != "active" for i in request.validated["tender"].lots if i.id == request.validated["award"].lotID]
    ):
        raise_operation_error(
            request, "Can {} document only in active lot status".format(OPERATIONS.get(request.method))
        )


def validate_update_contract_value(request, name="value", attrs=("currency",), **kwargs):
    data = request.validated["data"]
    value = data.get(name)
    if value:
        for ro_attr in attrs:
            field = getattr(request.context, name)
            if field and value.get(ro_attr) != field.to_native().get(ro_attr):
                raise_operation_error(request, "Can't update {} for contract {}".format(ro_attr, name), name=name)


def validate_update_contract_value_net_required(request, name="value", **kwargs):
    data = request.validated["data"]
    value = data.get(name)
    if value is not None and requested_fields_changes(request, (name, "status")):
        contract_amount_net = value.get("amountNet")
        if contract_amount_net is None:
            raise_operation_error(request, dict(amountNet=BaseType.MESSAGES["required"]), status=422, name=name)


def validate_update_contract_value_amount(request, name="value", **kwargs):
    data = request.validated["data"]
    contract_value = data.get(name)
    value = data.get("value") or data.get(name)
    if contract_value and requested_fields_changes(request, (name, "status")):
        amount = to_decimal(contract_value.get("amount"))
        amount_net = to_decimal(contract_value.get("amountNet"))
        tax_included = contract_value.get("valueAddedTaxIncluded")

        if not (amount == 0 and amount_net == 0):
            if tax_included:
                amount_max = (amount_net * AMOUNT_NET_COEF).quantize(Decimal("1E-2"), rounding=ROUND_UP)
                if (amount < amount_net or amount > amount_max):
                    raise_operation_error(
                        request,
                        "Amount should be equal or greater than amountNet and differ by "
                        "no more than {}%".format(AMOUNT_NET_COEF * 100 - 100),
                        name=name,
                    )
            else:
                if amount != amount_net:
                    raise_operation_error(request, "Amount and amountNet should be equal", name=name)

def validate_contract_items_unit_value_amount(request, contract, **kwargs):
    items_unit_value_amount = []
    for item in contract.items:
        if item.unit and item.quantity is not None:
            if item.unit.value:
                if item.quantity == 0 and item.unit.value.amount != 0:
                    raise_operation_error(
                        request, "Item.unit.value.amount should be updated to 0 if item.quantity equal to 0"
                    )
                items_unit_value_amount.append(
                    to_decimal(item.quantity) * to_decimal(item.unit.value.amount)
                )

    if items_unit_value_amount and contract.value:
        calculated_value = sum(items_unit_value_amount)

        if calculated_value.quantize(Decimal("1E-2"), rounding=ROUND_FLOOR) > to_decimal(contract.value.amount):
            raise_operation_error(
                request, "Total amount of unit values can't be greater than contract.value.amount"
            )


def validate_ua_road(classification_id, additional_classifications):
    road_count = sum([1 for i in additional_classifications if i["scheme"] == UA_ROAD_SCHEME])
    if is_ua_road_classification(classification_id):
        if road_count > 1:
            raise ValidationError(
                "Item shouldn't have more than 1 additionalClassification with scheme {}".format(UA_ROAD_SCHEME)
            )
    elif road_count != 0:
        raise ValidationError(
            "Item shouldn't have additionalClassification with scheme {} "
            "for cpv not starts with {}".format(UA_ROAD_SCHEME, ", ".join(UA_ROAD_CPV_PREFIXES))
        )


def validate_gmdn(classification_id, additional_classifications):
    gmdn_count = sum([1 for i in additional_classifications if i["scheme"] in (GMDN_2023_SCHEME, GMDN_2019_SCHEME)])
    if is_gmdn_classification(classification_id):
        inn_anc_count = sum([1 for i in additional_classifications if i["scheme"] in [INN_SCHEME, ATC_SCHEME]])
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
            "Item shouldn't have additionalClassification with scheme {} "
            "for cpv not starts with {}".format(GMDN_2019_SCHEME, ", ".join(GMDN_CPV_PREFIXES))
        )


def validate_milestones(value):
    if isinstance(value, list):
        sums = defaultdict(Decimal)
        for milestone in value:
            if milestone["type"] == "financing":
                percentage = milestone.get("percentage")
                if percentage:
                    sums[milestone.get("relatedLot")] += to_decimal(percentage)

        for uid, sum_value in sums.items():
            if sum_value != Decimal("100"):
                raise ValidationError(
                    "Sum of the financial milestone percentages {} is not equal 100{}.".format(
                        sum_value, " for lot {}".format(uid) if uid else ""
                    )
                )


def validate_procurement_type_of_first_stage(request, **kwargs):
    tender = request.validated["tender"]
    if tender.procurementMethodType not in FIRST_STAGE_PROCUREMENT_TYPES:
        request.errors.add(
            "body",
            "procurementMethodType",
            "Should be one of the first stage values: {}".format(FIRST_STAGE_PROCUREMENT_TYPES),
        )
        request.errors.status = 422
        raise error_handler(request)


def validate_tender_matches_plan(request, **kwargs):
    plan = request.validated["plan"]
    tender = request.validated.get("tender") or request.validated.get("tender_data")

    plan_identifier = plan.procuringEntity.identifier
    tender_identifier = tender.get("procuringEntity", {}).get("identifier", {})
    if plan.tender.procurementMethodType == "centralizedProcurement" and plan_identifier.id == "01101100":
        plan_identifier = plan.buyers[0].identifier

    if plan_identifier.id != tender_identifier.get("id") or plan_identifier.scheme != tender_identifier.get("scheme"):
        request.errors.add(
            "body",
            "procuringEntity",
            "procuringEntity.identifier doesn't match: {} {} != {} {}".format(
                plan_identifier.scheme, plan_identifier.id, tender_identifier["scheme"], tender_identifier["id"]
            ),
        )

    pattern = plan.classification.id[:3] if plan.classification.id.startswith("336") else plan.classification.id[:4]
    for i, item in enumerate(tender.get("items", "")):
        # item.classification may be empty in pricequotaiton
        if item.get("classification") and item["classification"]["id"][: len(pattern)] != pattern:
            request.errors.add(
                "body",
                "items[{}].classification.id".format(i),
                "Plan classification.id {} and item's {} should be of the same group {}".format(
                    plan.classification.id, item["classification"]["id"], pattern
                ),
            )

    if request.errors:
        request.errors.status = 422
        raise error_handler(request)


def validate_tender_plan_procurement_method_type(request, **kwargs):
    plan = request.validated["plan"]
    tender = request.validated["tender_data"]
    tender_type = tender.get("procurementMethodType")

    if plan.tender.procurementMethodType not in (tender_type, "centralizedProcurement"):
        if tender_type == PQ and plan.tender.procurementMethodType == "belowThreshold":
            return
        request.errors.add(
            "body",
            "procurementMethodType",
            "procurementMethodType doesn't match: {} != {}".format(
                plan.tender.procurementMethodType, tender_type
            ),
        )
        request.errors.status = 422
        raise error_handler(request)


def validate_plan_budget_breakdown(request, **kwargs):
    plan = request.validated["plan"]

    if not plan.budget or not plan.budget.breakdown:
        request.errors.add("body", "budget.breakdown", "Plan should contain budget breakdown")
        request.errors.status = 422
        raise error_handler(request)


def validate_tender_in_draft(request, **kwargs):
    if request.validated["tender"].status != "draft":
        raise raise_operation_error(request, "Only allowed in draft tender status")


def validate_procurement_kind_is_central(request, **kwargs):
    kind = "central"
    if request.validated["tender"].procuringEntity.kind != kind:
        raise raise_operation_error(request, "Only allowed for procurementEntity.kind = '{}'".format(kind))


def validate_tender_plan_data(request, **kwargs):
    data = validate_data(request, type(request.tender).plans.model_class)
    plan_id = data["id"]
    update_logging_context(request, {"plan_id": plan_id})

    plan = request.extract_plan(plan_id)
    with handle_data_exceptions(request):
        plan.validate()
    request.validated["plan"] = plan
    request.validated["plan_src"] = plan.serialize("plain")


# TODO: in future replace this types with strictTypes
#  (StrictStringType, StrictIntType, StrictDecimalType, StrictBooleanType)

TYPEMAP = {
    'string': StringType(),
    'integer': IntType(),
    'number': DecimalType(),
    'boolean': BooleanType(),
    'date-time': DateTimeType(),
}

# Criteria


def validate_value_factory(type_map):
    def validator(value, datatype):

        if value is None:
            return
        type_ = type_map.get(datatype)
        if not type_:
            raise ValidationError(
                'Type mismatch: value {} does not confront type {}'.format(
                    value, type_
                )
            )
        # validate value
        return type_.to_native(value)
    return validator


validate_value_type = validate_value_factory(TYPEMAP)


# tender.criterion.requirementGroups
def validate_requirement_values(requirement):
    expected = requirement.get('expectedValue')
    min_value = requirement.get('minValue')
    max_value = requirement.get('maxValue')

    if any((expected and min_value, expected and max_value)):
        raise ValidationError(
            'expectedValue conflicts with ["minValue", "maxValue"]'
        )

def check_requirements_active(criterion):
    for rg in criterion.get("requirementGroups", []):
        for requirement in rg.get("requirements", []):
            if requirement.get("status", "") == "active":
                return True
    return False
