from logging import getLogger
from openprocurement.api.utils import handle_store_exceptions, context_unpack
from openprocurement.api.context import get_now
from openprocurement.api.procedure.utils import (
    append_revision,
    get_revision_changes,
)

LOGGER = getLogger(__name__)


def save_plan(request, modified: bool = True, insert: bool = False) -> bool:
    plan = request.validated["plan"]

    patch = get_revision_changes(plan, request.validated["plan_src"])
    if patch:
        now = get_now()
        append_revision(request, plan, patch)

        old_date_modified = plan.get("dateModified", now.isoformat())
        if modified:
            plan["dateModified"] = now.isoformat()

        with handle_store_exceptions(request):
            request.registry.mongodb.plans.save(
                plan,
                insert=insert,
            )
            LOGGER.info(
                "Saved plan {}: dateModified {} -> {}".format(plan["_id"], old_date_modified, plan["dateModified"]),
                extra=context_unpack(
                    request,
                    {"MESSAGE_ID": "save_plan"},
                    {"RESULT": plan["_rev"]},
                ),
            )
            return True
    return False
