# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
)
from openprocurement.api.views.base import BaseResource
from openprocurement.tender.core.utils import save_tender, apply_patch


class BaseRequirementResponseEvidenceResource(BaseResource):

    def pre_save(self):
        pass

    def collection_post(self):
        context_name = self.request.context["__parent__"].__class__.__name__.lower()
        evidence = self.request.validated["evidence"]
        self.request.context.evidences.append(evidence)
        self.pre_save()
        if save_tender(self.request, validate=True):
            self.LOGGER.info(
                "Created {} requirement response evidence {}".format(context_name, evidence.id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "{}_requirement_response_evidence_create".format(context_name)},
                    {"evidence_id": evidence.id},
                ),
            )
            self.request.response.status = 201
            evidence_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers["Location"] = self.request.current_route_url(
                _route_name=evidence_route, evidence_id=evidence.id, _query={}
            )
            return {"data": evidence.serialize("view")}

    def collection_get(self):
        return {"data": [i.serialize("view") for i in self.request.context.evidences]}

    def get(self):
        return {"data": self.request.context.serialize("view")}

    def patch(self):
        evidence = self.request.context
        context_name = self.request.context["__parent__"]["__parent__"].__class__.__name__.lower()
        apply_patch(self.request, save=False, src=evidence.serialize())

        self.pre_save()
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated {} requirement response evidence {}".format(context_name, evidence.id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "{}_requirement_response_evidence_patch".format(context_name)}
                ),
            )
            return {"data": evidence.serialize("view")}

    def delete(self):
        evidence = self.request.context
        context_name = evidence["__parent__"]["__parent__"].__class__.__name__.lower()
        res = evidence.serialize("view")

        self.request.validated["requirement_response"].evidences.remove(evidence)
        self.pre_save()
        if save_tender(self.request):
            self.LOGGER.info(
                "Deleted {} evidence {}".format(context_name, self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "{}_evidence_delete".format(context_name)}),
            )
            return {"data": res}
