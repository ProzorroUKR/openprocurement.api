from cornice.resource import resource
from jsonpatch import apply_patch
from pyramid.security import Allow, Everyone

from openprocurement.api.utils import error_handler, json_view
from openprocurement.api.views.base import BaseResource


@resource(
    name="Plan History Resource",
    path="/history/plans/{plan_id}",
    description="Plan History Details",
)
class PlanHistoryResource(BaseResource):
    allowed_fields = {
        "rationale",
        # "additionalClassifications",
    }

    def __acl__(self):
        return [(Allow, Everyone, "view_plan")]

    @json_view(permission="view_plan")
    def get(self):
        request = self.request
        match_dict = request.matchdict
        if match_dict and match_dict.get("plan_id"):
            plan_id = match_dict["plan_id"]
            opt_fields = set(self.request.params.get("opt_fields", "").split(",")) & self.allowed_fields
            if not opt_fields:
                opt_fields = self.allowed_fields

            doc = request.registry.mongodb.plans.get_field_history(plan_id, *opt_fields)
            if doc:
                history = []
                actual_data = {k: doc.get(k) for k in opt_fields}
                revisions = doc.get("revisions") or []
                for rev in reversed(revisions):
                    # filter changes
                    changes = [c for c in rev["changes"] if c["path"].split("/")[1] in opt_fields]
                    if changes:
                        # apply changes and proceed
                        history.append(
                            {
                                "date": rev["date"],
                                "data": actual_data,
                            }
                        )
                        actual_data = apply_patch(actual_data, changes)
                # history already in the desc order
                descending = bool(self.request.params.get("descending", ""))
                if not descending:
                    history = list(reversed(history))
                return {"data": {"changes": history}}

        request.errors.add("url", "plan_id", "Not Found")
        request.errors.status = 404
        raise error_handler(request)
