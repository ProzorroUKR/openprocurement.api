# -*- coding: utf-8 -*-
from functools import partial
from zope.interface import implementer
from zope.component import queryUtility
from cornice.resource import resource
from openprocurement.api.utils import (
    error_handler,
    APIResourceListing
    )
from openprocurement.agreement.core.traversal import factory
from openprocurement.agreement.core.interfaces import IAgreementBuilder
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


@implementer(IAgreementBuilder)
class AgreementBuilder(object):

    def __init__(self, model):
        self.model = model

    def __call__(self, data, create=True):
        if create:
            return self.model(data)
        return self.model


baseCFABuilder = AgreementBuilder(Agreement)


class IsAgreenent(object):
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


def extract_agreement(request):
    db = request.registry.db
    agreement_id = request.matchdict['agreement_id']
    doc = db.get(agreement_id)
    configurator = request.content_configurator
    if doc is not None and doc.get('doc_type') == 'agreement':
        request.errors.add('url', 'agreement_id', 'Archived')
        request.errors.status = 410
        raise error_handler(request.errors)
    elif doc is None or doc.get('doc_type') != 'Agreement':
        request.errors.add('url', 'agreement_id', 'Not Found')
        request.errors.status = 404
        raise error_handler(request.errors)
    builder = queryUtility(
        IAgreementBuilder,
        name=configurator.agreement_type
        )
    if not builder or not doc.get('agreemenType'):
        request.errors.add('data', 'agreementType', 'Not implemented')
        request.errors.status = 415
        raise error_handler(request.errors)
    return builder(doc)      


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