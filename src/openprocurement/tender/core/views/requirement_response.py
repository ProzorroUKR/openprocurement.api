# -*- coding: utf-8 -*-
from openprocurement.api.utils import context_unpack, APIResource
from openprocurement.tender.core.utils import save_tender, apply_patch


class BaseRequirementResponseResource(APIResource):

    def collection_post(self):

        requirement_responses = self.request.validated["requirementresponses"]
        self.request.context.requirementResponses.extend(requirement_responses)

        context_name = self.request.context.__class__.__name__.lower()

        if save_tender(self.request):
            for requirement_response in requirement_responses:
                self.LOGGER.info(
                    "Created {} requirement response {}".format(context_name, requirement_response.id),
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": "{}_requirement_response_create".format(context_name)},
                        {"requirement_response_id": requirement_response.id},
                    ),
                )
                self.request.response.status = 201

            return {"data": [i.serialize("view") for i in requirement_responses]}

    def collection_get(self):
        return {"data": [i.serialize("view") for i in self.request.context.requirementResponses]}

    def get(self):
        return {"data": self.request.context.serialize("view")}

    def patch(self):
        requirement_response = self.request.context
        context_name = self.request.context["__parent__"].__class__.__name__.lower()
        apply_patch(self.request, save=False, src=requirement_response.serialize())

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated {} requirement response {}".format(context_name, requirement_response.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "{}_requirement_response_patch".format(context_name)}),
            )
            return {"data": requirement_response.serialize("view")}

    def delete(self):
        rr = self.request.context
        context_name = rr["__parent__"].__class__.__name__.lower()
        res = rr.serialize("view")

        self.request.validated[context_name].requirementResponses.remove(rr)
        self.request.validated["tender"].modified = False
        if save_tender(self.request):
            self.LOGGER.info(
                "Deleted {} requirement response {}".format(context_name, self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "{}_requirement_response_delete".format(context_name)}),
            )
            return {"data": res}
