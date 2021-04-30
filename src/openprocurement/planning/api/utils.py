# -*- coding: utf-8 -*-
from functools import partial
from logging import getLogger
from time import sleep
from cornice.resource import resource
from couchdb.http import ResourceConflict
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
from openprocurement.planning.api.models import Plan
from openprocurement.planning.api.traversal import factory

LOGGER = getLogger("openprocurement.planning.api")


def generate_plan_id(ctime, db, server_id=""):
    """ Generate ID for new plan in format "UA-P-YYYY-MM-DD-NNNNNN" + ["-server_id"]
        YYYY - year, MM - month (start with 1), DD - day, NNNNNN - sequence number per 1 day
        and save plans count per day in database document with _id = "planID" as { key, value } = { "2015-12-03": 2 }
    :param ctime: system date-time
    :param db: couchdb database object
    :param server_id: server mark (for claster mode)
    :return: planID in "UA-2015-05-08-000005"
    """
    key = ctime.date().isoformat()  # key (YYYY-MM-DD)
    plan_id_doc = "planID_" + server_id if server_id else "planID"  # document _id
    index = 1
    while True:
        try:
            plan_id = db.get(plan_id_doc, {"_id": plan_id_doc})  # find root document
            index = plan_id.get(key, 1)
            plan_id[key] = index + 1  # count of plans in db (+1 ?)
            db.save(plan_id)
        except ResourceConflict:  # pragma: no cover
            pass
        except Exception:  # pragma: no cover
            sleep(1)
        else:
            break
    return "UA-P-{:04}-{:02}-{:02}-{:06}{}".format(
        ctime.year, ctime.month, ctime.day, index, server_id and "-" + server_id
    )


def plan_serialize(request, plan_data, fields):
    plan = request.plan_from_data(plan_data, raise_error=False)
    plan.__parent__ = request.context
    return dict([(i, j) for i, j in plan.serialize("view").items() if i in fields])


def save_plan(request):
    """ Save plan object to database
    :param request:
    :return: True if Ok
    """
    plan = request.validated["plan"]

    patch = get_revision_changes(plan.serialize("plain"), request.validated["plan_src"])
    if patch:
        append_revision(request, plan, patch)
        old_date_modified = plan.dateModified

        if getattr(plan, "modified", True):
            now = get_now()
            plan.dateModified = now
            if any(c for c in patch if c["path"].startswith("/cancellation/")):
                plan.cancellation.date = now

        with handle_store_exceptions(request):
            plan.store(request.registry.databases.plans)
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


class APIResource(object):
    def __init__(self, request, context):
        self.context = context
        self.request = request
        self.db = request.registry.databases.plans
        self.server_id = request.registry.server_id
        self.server = request.registry.couchdb_server
        self.update_after = request.registry.update_after
        self.LOGGER = getLogger(type(self).__module__)


def set_logging_context(event):
    request = event.request
    params = {}
    if "plan" in request.validated:
        params["PLAN_REV"] = request.validated["plan"].rev
        params["PLANID"] = request.validated["plan"].planID
    update_logging_context(request, params)


def extract_plan_doc(request, plan_id=None):
    plan_id = plan_id or request.matchdict["plan_id"]
    db = request.registry.databases.plans
    doc = db.get(plan_id)
    if doc is not None and doc.get("doc_type") == "plan":
        request.errors.add("url", "plan_id", "Archived")
        request.errors.status = 410
        raise error_handler(request)
    if doc is None or doc.get("doc_type") != "Plan":
        request.errors.add("url", "plan_id", "Not Found")
        request.errors.status = 404
        raise error_handler(request)
    return doc


def extract_plan(request, plan_id=None):
    doc = extract_plan_doc(request, plan_id)
    if doc:
        return request.plan_from_data(doc)


def plan_from_data(request, data, raise_error=True, create=True):
    if create:
        return Plan(data)
    return Plan
