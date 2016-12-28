from cornice.resource import resource
from functools import partial
from logging import getLogger

from openprocurement.api.utils import error_handler
from openprocurement.historical.tender.traversal import tender_historical_factory
from openprocurement.historical.core.utils import (
    extract_doc,
    apply_while,
)


tenders_history_resource = partial(resource,
                                   error_handler=error_handler,
                                   factory=tender_historical_factory)
logger = getLogger(__name__)

def extract_tender_version(request):
    tender = extract_doc(request,
                         request.matchdict['tender_id'],
                         'Tender')

    public_revisions = [
        rev
        for rev in tender.get('revisions', [])
        if rev.get('public', False)
    ]

    if not public_revisions:
        request.add_header('0')
        return request.tender_from_data(tender)

    current_version = len(public_revisions)

    revision_index = request.extract_header()
    if not revision_index:
        revision_index = current_version

    if revision_index >= current_version or revision_index <= 0:
        request.add_header(current_version)
        return request.tender_from_data(tender)
    else:
        revisions = tender['revisions']
        tender = request.tender_from_data(tender).serialize('plain')
        revision = public_revisions[revision_index]
        tender_version = apply_while(tender, revisions, revision['rev'])
        tender_version['dateModified'] = public_revisions[revision_index - 1].get('date')
        request.add_header(revision_index)
        return request.tender_from_data(tender_version)
