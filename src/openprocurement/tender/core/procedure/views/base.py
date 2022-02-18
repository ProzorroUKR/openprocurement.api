from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.context import set_request, set_now
from copy import deepcopy
from logging import getLogger
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS


class TenderBaseResource:

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
        self.request = request
        self.db = request.registry.db
        self.server_id = request.registry.server_id
        self.LOGGER = getLogger(type(self).__module__)
        # init state class that handles tender business logic
        self.state = self.state_class(request)

        # https://github.com/Cornices/cornice/issues/479#issuecomment-388407385
        # init is called twice (with and without context), thanks to cornice.
        if not context:
            # common stuff, can be the same for plans, contracts, etc
            set_request(request)
            set_now()
            # getting tender
            match_dict = request.matchdict
            if match_dict and match_dict.get("tender_id"):
                request.validated["tender_src"] = request.tender_doc
                request.validated["tender"] = deepcopy(request.validated["tender_src"])
