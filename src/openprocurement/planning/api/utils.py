from logging import getLogger
from openprocurement.api.utils import get_now, error_handler
from openprocurement.api.mask import mask_object_data

LOGGER = getLogger("openprocurement.planning.api")


def generate_plan_id(request, server_id=""):
    """ Generate ID for new plan in format "UA-P-YYYY-MM-DD-NNNNNN" + ["-server_id"]
        YYYY - year, MM - month (start with 1), DD - day, NNNNNN - sequence number per 1 day
        and save plans count per day in database document with _id = "planID" as { key, value } = { "2015-12-03": 2 }
    :param request:
    :param server_id: server mark (for claster mode)
    :return: planID in "UA-2015-05-08-000005"
    """
    now = get_now()
    uid = f"plan_{server_id}_{now.date().isoformat()}"
    index = request.registry.mongodb.get_next_sequence_value(uid)
    return "UA-P-{:04}-{:02}-{:02}-{:06}{}".format(
        now.year, now.month, now.day, index, server_id and "-" + server_id
    )


def extract_plan_doc(request, plan_id=None):
    plan_id = plan_id or request.matchdict["plan_id"]
    doc = request.registry.mongodb.plans.get(plan_id)
    if doc is None:
        request.errors.add("url", "plan_id", "Not Found")
        request.errors.status = 404
        raise error_handler(request)

    mask_object_data(request, doc)  # war time measures

    return doc
