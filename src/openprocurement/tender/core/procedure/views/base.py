from pyramid.security import ALL_PERMISSIONS, Allow, Everyone

from openprocurement.api.utils import request_fetch_agreement, request_init_tender
from openprocurement.api.views.base import BaseResource
from openprocurement.tender.core.procedure.state.tender import TenderState


class TenderBaseResource(BaseResource):
    state_class = TenderState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_tender"),
            (Allow, "g:brokers", "edit_tender"),
            (Allow, "g:Administrator", "edit_tender"),
            (Allow, "g:admins", ALL_PERMISSIONS),  # some tests use this, idk why
            (Allow, "g:auction", "auction"),
            (Allow, "g:chronograph", "chronograph"),
            (Allow, "g:contracting", "extract_credentials"),
            (Allow, "g:competitive_dialogue", "extract_credentials"),
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
                tender = request_init_tender(request, request.tender_doc)

                if request.method not in ("GET", "HEAD"):
                    if tender["config"]["hasPreSelectionAgreement"] is True:
                        agreements = [tender["agreement"]] if tender.get("agreement") else tender.get("agreements")
                        if agreements and "agreement" not in request.validated:
                            request_fetch_agreement(request, agreements[0]["id"], raise_error=False)
