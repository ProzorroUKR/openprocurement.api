# -*- coding: utf-8 -*-
from functools import partial
from zope.interface import implementer
from cornice.resource import resource
from openprocurement.api.utils import (
    error_handler,
    APIResourceListing
    )
from openprocurement.agreement.core.traversal import factory
from openprocurement.agreement.core.models.agreement import Agreement
from openprocurement.agreement.core.design import (
    FIELDS,
    agreements_all_view,
    agreements_by_dateModified_view,
    agreements_real_by_dateModified_view,
    agreements_test_by_dateModified_view,
    agreements_by_local_seq_view,
    agreements_real_by_local_seq_view,
    agreements_test_by_local_seq_view
    )
from openprocurement.agreement.core.utils import agreement_serialize


agreements_resource = partial(
    resource,
    factory=factory,
    error_handler=error_handler
)
VIEW_MAP = {
    u'': agreements_real_by_dateModified_view,
    u'test': agreements_test_by_dateModified_view,
    u'_all_': agreements_by_dateModified_view,
}
CHANGES_VIEW_MAP = {
    u'': agreements_real_by_local_seq_view,
    u'test': agreements_test_by_local_seq_view,
    u'_all_': agreements_by_local_seq_view,
}
FEED = {
    u'dateModified': VIEW_MAP,
    u'changes': CHANGES_VIEW_MAP,
}


class IsAgreement(object):
    """ Route predicate. """

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'agreementType = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        if request.agreement is not None:
            c_type = getattr(request.contract, 'agreementType',
                             None) or "cfa"
            return c_type == self.val
        return False




class AgreementsResource(APIResourceListing):

    def __init__(self, request, context):
        super(AgreementsResource, self).__init__(request, context)
        # params for listing
        self.VIEW_MAP = VIEW_MAP
        self.CHANGES_VIEW_MAP = CHANGES_VIEW_MAP
        self.FEED = FEED
        self.FIELDS = FIELDS
        self.serialize_func = agreement_serialize
        self.object_name_for_listing = 'Agreements'
        self.log_message_id = 'agreement_list_custom'