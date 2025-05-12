from openprocurement.api.procedure.utils import (
    append_revision,
    get_revision_changes,
    save_object,
)


def save_plan(request, modified: bool = True, insert: bool = False) -> bool:
    obj = request.validated["plan"]
    obj_src = request.validated["plan_src"]

    patch = get_revision_changes(obj, obj_src)
    if not patch:
        return False

    append_revision(request, obj, patch)

    return save_object(request, "plan", modified, insert)
