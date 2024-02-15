from pyramid.security import Allow, ALL_PERMISSIONS

from openprocurement.api.utils import request_init_object, request_init_transfer
from openprocurement.api.views.base import BaseResource


class TransferBaseResource(BaseResource):
    def __acl__(self):
        acl = [
            (Allow, "g:brokers", "view_transfer"),
            (Allow, "g:brokers", "create_transfer"),
            (Allow, "g:admins", ALL_PERMISSIONS),
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)
        # https://github.com/Cornices/cornice/issues/479#issuecomment-388407385
        # init is called twice (with and without context), thanks to cornice.
        if not context:
            match_dict = request.matchdict
            if match_dict and match_dict.get("transfer_id"):
                request_init_transfer(request, request.transfer_doc)
