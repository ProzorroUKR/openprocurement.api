from typing import Type

from pyramid.security import Allow, Everyone

from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource


class SignResourceMixin:
    serializer_class = Type[BaseSerializer]
    obj_name: str
    context_objs: dict

    def fetch_context(self):
        context = {}
        for parent_name, parent_serializer_class in self.context_objs.items():
            if parent_obj := self.request.validated.get(parent_name):
                context[parent_name] = parent_serializer_class(parent_obj).data
        return context

    @json_view(
        permission="view_tender",
    )
    def get(self):
        data = self.serializer_class(self.request.validated[self.obj_name]).data
        context = self.fetch_context()
        return {
            "data": data,
            "context": context,
        }


class BaseSignResource(SignResourceMixin, TenderBaseResource):
    context_objs = {
        "tender": TenderBaseSerializer,
    }

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
        ]
        return acl
