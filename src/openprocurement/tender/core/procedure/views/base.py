from openprocurement.api.views.base import BaseResource
from openprocurement.tender.core.procedure.serializers.config import TenderConfigSerializer
from openprocurement.tender.core.procedure.state.tender import TenderState
from copy import deepcopy
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS


class TenderBaseResource(BaseResource):

    serializer_config_class = TenderConfigSerializer
    state_class = TenderState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_tender"),
            (Allow, "g:brokers", "edit_tender"),
            (Allow, "g:Administrator", "edit_tender"),

            (Allow, "g:admins", ALL_PERMISSIONS),    # some tests use this, idk why

            (Allow, "g:auction", "auction"),
            (Allow, "g:chronograph", "chronograph"),
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)
        # init state class that handles tender business logic
        self.state = self.state_class(request)

        # https://github.com/Cornices/cornice/issues/479#issuecomment-388407385
        # init is called twice (with and without context), thanks to cornice.
        if not context:
            # getting tender
            match_dict = request.matchdict
            if match_dict and match_dict.get("tender_id"):
                request.validated["tender_src"] = request.tender_doc
                request.validated["tender"] = deepcopy(request.validated["tender_src"])
                tender_config = request.validated["tender"].pop("config", None) or {}
                self._serialize_config(request, tender_config)

    def _serialize_config(self, request, config):
        request.validated["tender_config"] = self.serializer_config_class(config).data
