from functools import partial
from logging import getLogger
from cornice.resource import resource
from openprocurement.api.utils import (
    update_logging_context,
    context_unpack,
    get_revision_changes,
    get_now,
    apply_data_patch,
    error_handler,
    handle_store_exceptions,
    append_revision,
)
from openprocurement.api.mask import mask_object_data
from openprocurement.planning.api.models import Plan
from openprocurement.planning.api.traversal import factory

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


def save_plan(request, insert=False):
    """ Save plan object to database
    :param request:
    :param insert:
    :return: True if Ok
    """
    plan = request.validated["plan"]

    patch = get_revision_changes(plan.serialize("plain"), request.validated["plan_src"])
    if patch:
        append_revision(request, plan, patch)
        old_date_modified = plan.dateModified

        modified = getattr(plan, "is_modified", True)
        if modified:
            now = get_now()
            if any(c for c in patch if c["path"].startswith("/cancellation/")):
                plan.cancellation.date = now

        with handle_store_exceptions(request):
            request.registry.mongodb.plans.save(
                plan,
                insert=insert,
                modified=modified,
            )
            LOGGER.info(
                "Saved plan {}: dateModified {} -> {}".format(
                    plan.id,
                    old_date_modified and old_date_modified.isoformat(),
                    plan.dateModified.isoformat()
                ),
                extra=context_unpack(request, {"MESSAGE_ID": "save_plan"}, {"PLAN_REV": plan.rev}),
            )
            return True


def apply_patch(request, data=None, save=True, src=None):
    data = request.validated["data"] if data is None else data
    patch = data and apply_data_patch(src or request.context.serialize(), data)
    if patch:
        request.context.import_data(patch)
        if save:
            return save_plan(request)
        if get_revision_changes(request.validated["plan"].serialize("plain"), request.validated["plan_src"]):
            return True  # should return True if there're any actual changes (either save = True or False


opresource = partial(resource, error_handler=error_handler, factory=factory)


def set_logging_context(event):
    request = event.request
    params = {}
    if "plan" in request.validated:
        params["PLAN_REV"] = request.validated["plan"].rev
        params["PLANID"] = request.validated["plan"].planID
    update_logging_context(request, params)


def extract_plan_doc(request, plan_id=None):
    plan_id = plan_id or request.matchdict["plan_id"]
    doc = request.registry.mongodb.plans.get(plan_id)
    if doc is None:
        request.errors.add("url", "plan_id", "Not Found")
        request.errors.status = 404
        raise error_handler(request)

    mask_object_data(request, doc)  # war time measures

    return doc


def extract_plan(request, plan_id=None):
    doc = extract_plan_doc(request, plan_id)
    if doc:
        return request.plan_from_data(doc)


def plan_from_data(request, data, raise_error=True, create=True):
    if create:
        return Plan(data)
    return Plan
