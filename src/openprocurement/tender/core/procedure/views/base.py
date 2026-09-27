from pyramid.security import ALL_PERMISSIONS, Allow, Everyone

from openprocurement.api.utils import request_fetch_agreement, request_init_tender
from openprocurement.api.views.base import BaseResource
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.utils import ProcurementMethodTypePredicate


class TenderBaseResource(BaseResource):
    state_class = TenderState
    # {procurementMethodType: state class} for resources shared by several procurement method types;
    # a value may also be a resolver called with the request (e.g. competitiveOrdering: the state depends
    # on the agreement), which is why the state is created lazily, after the tender is loaded
    state_classes = None

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
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)
        self._state = None

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

    @property
    def state(self):
        """
        the state that handles the tender business logic

        The class is resolved on every access: a resolver may give another class once the tender data
        is loaded (competitiveOrdering: the agreement is fetched during the tender creation).
        """
        state_class = self.get_state_class(self.request)
        if state_class is None:
            return None
        if self._state is None or type(self._state) is not state_class:
            self._state = state_class(self.request)
        return self._state

    def get_state_class(self, request):
        if self.state_classes:
            state_class = self.state_classes[ProcurementMethodTypePredicate.procurement_method_type(request)]
            if not isinstance(state_class, type):  # a resolver
                state_class = state_class(request)
            return state_class
        return self.state_class
