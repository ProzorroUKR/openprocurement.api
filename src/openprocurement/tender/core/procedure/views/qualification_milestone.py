from cornice.resource import resource

from openprocurement.api.procedure.utils import get_items
from openprocurement.api.procedure.validation import (
    validate_input_data,
    validate_item_owner,
)
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.tender.core.procedure.models.qualification_milestone import (
    PostQualificationMilestone,
)
from openprocurement.tender.core.procedure.serializers.qualification_milestone import (
    QualificationMilestoneSerializer,
)
from openprocurement.tender.core.procedure.state.qualification_milestone import (
    QualificationMilestoneState,
)
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.validation import (
    validate_24h_milestone_released,
    validate_qualification_update_not_in_pre_qualification,
    validate_update_qualification_only_for_active_lots,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.views.qualification import (
    resolve_qualification,
)


def resolve_milestone(request, context_name: str = "qualification"):
    match_dict = request.matchdict
    milestone_id = match_dict.get("milestone_id")
    if milestone_id:
        milestones = get_items(request, request.validated[context_name], "milestones", milestone_id)
        request.validated["milestone"] = milestones[0]


class BaseMilestoneResource(TenderBaseResource):
    serializer_class = QualificationMilestoneSerializer
    state_class = QualificationMilestoneState

    context_name = "qualification"

    @json_view(permission="view_tender")
    def collection_get(self):
        obj = self.request.validated[self.context_name]
        data = tuple(self.serializer_class(milestone).data for milestone in obj.get("milestones", ""))
        return {"data": data}

    @json_view(permission="view_tender")
    def get(self):
        data = self.serializer_class(self.request.validated["milestone"]).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_item_owner("tender"),
            validate_24h_milestone_released,
            validate_input_data(PostQualificationMilestone),
            validate_qualification_update_not_in_pre_qualification,
            validate_update_qualification_only_for_active_lots,
        ),
    )
    def collection_post(self):
        tender = self.request.validated["tender"]
        milestone = self.request.validated["data"]
        parent_obj = self.request.validated[self.context_name]

        self.state.validate_post(self.context_name, parent_obj, milestone)

        if "milestones" not in parent_obj:
            parent_obj["milestones"] = []
        parent_obj["milestones"].append(milestone)

        self.state.on_post(milestone)

        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender {} milestone {}".format(self.context_name, milestone["id"]),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_{}_milestone_create".format(self.context_name)},
                    {"milestone_id": milestone["id"]},
                ),
            )
            self.request.response.status = 201
            self.set_location(tender, milestone)
            return {"data": self.serializer_class(milestone).data}

    def set_location(self, tender, milestone):
        pass


@resource(
    name="Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    description="Tender qualification milestones",
)
class QualificationMilestoneResource(BaseMilestoneResource):
    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_qualification(request)
        resolve_milestone(request, context_name="qualification")

    def set_location(self, tender, milestone):
        parent_obj = self.request.validated[self.context_name]
        self.request.response.headers["Location"] = self.request.route_url(
            "Tender {} Milestones".format(self.context_name.capitalize()),
            **{
                "tender_id": tender["_id"],
                "{}_id".format(self.context_name): parent_obj["id"],
                "milestone_id": milestone["id"],
            },
        )
