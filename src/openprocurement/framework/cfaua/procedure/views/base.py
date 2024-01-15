from openprocurement.api.procedure.context import init_object
from openprocurement.api.views.base import BaseResource
from openprocurement.framework.cfaua.procedure.serializers.agreement import AgreementSerializer
from openprocurement.framework.cfaua.procedure.state.agreement import AgreementState
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS

from openprocurement.framework.core.procedure.serializers.agreement import AgreementConfigSerializer


class AgreementBaseResource(BaseResource):
    serializer_class = AgreementSerializer
    state_class = AgreementState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_listing"),
            (Allow, Everyone, "view_agreement"),
            (Allow, "g:agreements", "create_agreement"),
            (Allow, "g:contracting", "create_agreement"),
            (Allow, "g:Administrator", "edit_agreement"),
            (Allow, "g:brokers", "edit_agreement"),
            (Allow, "g:admins", ALL_PERMISSIONS),
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)
        # init state class that handles framework business logic
        self.state = self.state_class(request)

        # https://github.com/Cornices/cornice/issues/479#issuecomment-388407385
        # init is called twice (with and without context), thanks to cornice.
        if not context:
            # getting agreement
            match_dict = request.matchdict
            if match_dict and match_dict.get("agreement_id"):
                init_object("agreement", request.agreement_doc, config_serializer=AgreementConfigSerializer)
