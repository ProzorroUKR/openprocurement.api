from schematics.exceptions import ValidationError

from openprocurement.api.constants_env import PQ_CRITERIA_ID_FROM
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import get_first_revision_date, raise_operation_error
from openprocurement.tender.core.procedure.models.criterion import ReqStatuses
from openprocurement.tender.pricequotation.constants import PROFILE_PATTERN


def validate_bid_value(tender, value):
    if not value:
        raise ValidationError("This field is required.")
    config = get_tender()["config"]
    if config.get("valueCurrencyEquality"):
        if tender["value"].get("currency") != value.get("currency"):
            raise ValidationError("currency of bid should be identical to currency of value of tender")
        if config.get("hasValueRestriction") and tender["value"]["amount"] < value["amount"]:
            raise ValidationError("value of bid should be less than value of tender")
    if tender["value"].get("valueAddedTaxIncluded") != value.get("valueAddedTaxIncluded"):
        raise ValidationError(
            "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of tender"
        )


def validate_contract_document_status(operation):
    def validate(request, **_):
        tender_status = request.validated["tender"]["status"]
        if tender_status not in ["active.qualification", "active.awarded"]:
            raise_operation_error(
                request,
                f"Can't {operation} document in current ({tender_status}) tender status",
            )
        if request.validated["contract"]["status"] not in ["pending", "active"]:
            raise_operation_error(request, f"Can't {operation} document in current contract status")

    return validate


def validate_profile_pattern(profile):
    result = PROFILE_PATTERN.findall(profile)
    if len(result) != 1:
        raise ValidationError("The profile value doesn't match id pattern")


def validate_criteria_id_uniq(objs, *args):
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
