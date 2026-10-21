from logging import getLogger

from openprocurement.api.mask_deprecated import mask_object_data_deprecated
from openprocurement.api.utils import get_now, get_obj_by_id

LOGGER = getLogger("openprocurement.planning.api")


def generate_plan_id(request):
    """Generate ID for new plan in format "UA-P-YYYY-MM-DD-NNNNNN"
        YYYY - year, MM - month (start with 1), DD - day, NNNNNN - sequence number per 1 day
        and save plans count per day in database document with _id = "planID" as { key, value } = { "2015-12-03": 2 }
    :param request:
    :return: planID in "UA-2015-05-08-000005"
    """
    now = get_now()
    uid = f"plan_{now.date().isoformat()}"
    index = request.registry.mongodb.get_next_sequence_value(uid)
    return "UA-P-{:04}-{:02}-{:02}-{:06}-a".format(now.year, now.month, now.day, index)


def extract_plan_doc(request, plan_id=None, first_revision_only=None):
    plan_id = plan_id or request.matchdict["plan_id"]
    doc = get_obj_by_id(request, "plans", plan_id, first_revision_only=first_revision_only)

    mask_object_data_deprecated(request, doc)  # war time measures

    return doc
