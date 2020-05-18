# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    context_unpack, 
    json_view,
    APIResource,
)
from openprocurement.tender.core.validation import (
    validate_24h_milestone_released,
    validate_qualification_milestone_24hours,
    validate_qualification_milestone_data,
)
from openprocurement.tender.core.utils import save_tender


class BaseQualificationMilestoneResource(APIResource):

    context_name = "qualification"

    @json_view(permission="view_tender")
    def collection_get(self):
        return {"data": [i.serialize("view") for i in self.request.validated[self.context_name].milestones]}

    @json_view(permission="view_tender")
    def get(self):
        return {"data": self.request.validated["milestone"].serialize("view")}

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_24h_milestone_released,
            validate_qualification_milestone_data,
            validate_qualification_milestone_24hours,
        ),
    )
    def collection_post(self):
        tender = self.request.validated["tender"]
        milestone = self.request.validated["milestone"]
        self.context.milestones.append(milestone)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender {} milestone {}".format(self.context_name, milestone.id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_{}_milestone_create".format(self.context_name)},
                    {"bid_id": milestone.id}
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender {} Milestones".format(tender.procurementMethodType, self.context_name.capitalize()),
                **{
                    "tender_id": tender.id,
                    "{}_id".format(self.context_name): self.context.id,
                    "milestone_id": milestone.id
                }
            )
            return {"data": milestone.serialize("view")}
