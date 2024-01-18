from logging import getLogger

from openprocurement.api.utils import (
    json_view,
    context_unpack,
    update_logging_context)
from openprocurement.framework.core.procedure.serializers.milestone import MilestoneSerializer
from openprocurement.framework.core.procedure.state.milestone import MilestoneState
from openprocurement.framework.core.procedure.views.contract import resolve_contract
from openprocurement.api.procedure.context import get_object
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.api.procedure.utils import get_items, set_item

LOGGER = getLogger(__name__)


def resolve_milestone(request):
    match_dict = request.matchdict
    if match_dict.get("milestone_id"):
        milestones = get_items(request, request.validated["contract"], "milestones", match_dict["milestone_id"])
        request.validated["milestone"] = milestones[0]


class AgreementContractMilestonesResource(FrameworkBaseResource):
    serializer_class = MilestoneSerializer
    state_class = MilestoneState

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_contract(request)
            resolve_milestone(request)

    @json_view(
        permission="view_framework",
    )
    def collection_get(self):
        contract = self.request.validated["contract"]
        data = tuple(self.serializer_class(milestone).data for milestone in contract.get("milestones", []))
        return {"data": data}

    @json_view(
        permission="view_framework",
    )
    def get(self):
        return {"data": self.serializer_class(get_object("milestone")).data}

    def collection_post(self):
        update_logging_context(self.request, {"milestone_id": "__new__"})
        milestone = self.request.validated["data"]
        contract = self.request.validated["contract"]
        if "milestones" not in contract:
            contract["milestones"] = []
        contract["milestones"].append(milestone)
        self.state.on_post(milestone)
        set_item(self.request.validated["agreement"], "contracts", contract["id"], contract)

        if save_object(self.request, "agreement", insert=True):
            self.LOGGER.info(
                f"Updated agreement milestone {milestone['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": f"agreement_milestone_create"})
            )
            self.request.response.status = 201
            return {"data": self.serializer_class(milestone).data}

    def patch(self):
        updated = self.request.validated["data"]
        if updated:
            milestone = self.request.validated["milestone"]
            self.state.on_patch(milestone, updated)
            set_item(self.request.validated["contract"], "milestones", milestone["id"], updated)
            if save_object(self.request, "agreement"):
                self.LOGGER.info(
                    f"Updated agreement milestone {self.request.validated['milestone']['id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": f"agreement_milestone_patch"})
                )
                return {"data": self.serializer_class(updated).data}
