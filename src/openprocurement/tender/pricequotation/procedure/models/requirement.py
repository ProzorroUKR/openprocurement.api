from schematics.validate import ValidationError

from openprocurement.api.constants import PQ_CRITERIA_ID_FROM
from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import get_first_revision_date


def validate_criteria_id_uniq(objs, *args):
    if not objs:
        return
    tender = get_tender()
    if get_first_revision_date(tender, default=get_now()) > PQ_CRITERIA_ID_FROM:
        ids = [i.id for i in objs]
        if len(set(ids)) != len(ids):
            raise ValidationError("Criteria id should be uniq")

        rg_ids = [rg.id for c in objs for rg in c.requirementGroups or ""]
        if len(rg_ids) != len(set(rg_ids)):
            raise ValidationError("Requirement group id should be uniq in tender")

        req_ids = [req.id for c in objs for rg in c.requirementGroups or "" for req in rg.requirements or ""]
        if len(req_ids) != len(set(req_ids)):
            raise ValidationError("Requirement id should be uniq for all requirements in tender")
