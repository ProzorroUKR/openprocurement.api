from jsonpointer import JsonPointerException
from jsonpatch import JsonPatchException

from iso8601 import parse_date
from zope.interface import providedBy

from pyramid.view import _call_view
from pyramid.security import Allow
from pyramid.interfaces import IRouteRequest, IRoutesMapper

from openprocurement.historical.core.constants import (
    VERSION, HASH, PREVIOUS_HASH, ACCREDITATION_LEVEL, VERSION_BY_DATE
)
from openprocurement.api.utils import (
    error_handler,
    _apply_patch,
    APIResource,
    json_view,
    context_unpack
)


class Root(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
        (Allow, 'g:brokers', 'view_historical'),
        (Allow, 'g:Administrator', 'view_historical')
    ]

    def __init__(self, request):
        self.request = request
        self.db = request.registry.db


def get_version_from_date(request, doc, revisions):
    version_date = request.headers.get(VERSION_BY_DATE)

    if parse_date(version_date) > parse_date(doc['dateModified']) or \
            parse_date(version_date) < parse_date(revisions[1]['date']):
        return return404(request, 'header', 'hash')
    for version, patch in reversed(list(enumerate(revisions))):
        try:
            doc = _apply_patch(doc, patch['changes'])
        except (JsonPointerException, JsonPatchException):
            raise_not_implemented(request)
        if parse_date(version_date) < parse_date(patch['date']):
            continue
        else:
            if request.validated[HASH] and \
                                request.validated[HASH] != parse_hash(patch.get('rev')):
                    return return404(request, 'header', 'hash')
            doc['dateModified'] = find_dateModified(revisions[:version + 1])
            return (doc,
                    parse_hash(patch['rev']),
                    parse_hash(revisions[version - 1].get('rev', '')))
    return return404(request, 'header', 'hash')


def extract_doc(request, doc_type):
    doc_id = request.matchdict['doc_id']
    if doc_id is None:
        return404(request, 'url', '{}_id'.format(doc_type.lower()))  # pragma: no cover
    validate_header(request)
    doc = request.registry.db.get(doc_id)
    if doc is None or doc.get('doc_type') != doc_type:
        return404(request, 'url', '{}_id'.format(doc_type.lower()))

    revisions = doc.pop('revisions', [])

    if request.validated.get(VERSION_BY_DATE):
        doc, revision_hash, prev_hash = get_version_from_date(request, doc, revisions)
        add_responce_headers(request, version=request.validated[VERSION],
                             rhash=revision_hash, phash=prev_hash)
        return doc

    if not revisions or not request.validated.get(VERSION):
        add_responce_headers(request, version=str(len(revisions)),
                             rhash=parse_hash(doc.get('_rev', '')),
                             phash=parse_hash(
                                 revisions[-1].get('rev')
                                 if len(revisions) > 0 else ''
                             ))
        return doc

    if int(request.validated.get(VERSION)) > len(revisions):
        return404(request, 'header', 'version')

    doc, revision_hash, prev_hash = apply_while(request, doc, revisions)
    add_responce_headers(request,
                         version=request.validated[VERSION],
                         rhash=revision_hash, phash=prev_hash)
    return doc


def add_responce_headers(request, version='', rhash='', phash=''):
    request.response.headers[VERSION] = str(version) or\
                                        str(request.validated.get(VERSION, ''))
    request.response.headers[HASH] = str(rhash)
    request.response.headers[PREVIOUS_HASH] = str(phash)


def raise_not_implemented(request):
    request.errors.status = 501
    request.errors.add('tender', 'revision', 'Not Implemented')
    raise error_handler(request.errors)


def apply_while(request, doc, revisions):
    for version, patch in reversed(list(enumerate(revisions))):
        try:
            doc = _apply_patch(doc, patch['changes'])
        except (JsonPointerException, JsonPatchException):
            raise_not_implemented(request)
        if str(version) == request.validated[VERSION]:
            if request.validated[HASH] and\
               request.validated[HASH] != parse_hash(patch.get('rev')):
                return404(request, 'header', 'hash')

            doc['dateModified'] = find_dateModified(revisions[:version+1])
            return (doc,
                    parse_hash(patch['rev']),
                    parse_hash(revisions[version - 1].get('rev', '')))
    return404('header', 'version')


def find_dateModified(revisions):
    for patch in reversed(revisions):
        if not any(op.get('path') for op in patch.get('changes')
                   if 'bids' in op.get('path')):
            return patch.get('date')
    return ''


def get_route(request):
    registry = request.registry
    q = registry.queryUtility
    routes_mapper = q(IRoutesMapper)
    path = request.path.replace('/historical', '')
    for r in routes_mapper.routelist:
        match = r.match(path)
        if match is not None:
            preds = r.predicates
            info = {'match': match, 'route': r}
            if preds and not all((p(info, request) for p in preds)):
                continue  # pragma: no cover
            return info['route']
    return None


def call_view(request, context, route):
    registry = request.registry
    request.request_iface = registry.queryUtility(IRouteRequest,
                                                  name=route.name)
    return _call_view(registry, request,
                      context, providedBy(context), '', secure=True)


def return404(request, where, why):
    request.errors.add(where, why, 'Not Found')
    request.errors.status = 404
    raise error_handler(request.errors)


def parse_hash(rev_hash):
    if rev_hash and hasattr(rev_hash, 'split'):
        shash = rev_hash.split('-')
        if len(shash) > 1:
            return shash[1]
    return ''


def validate_header(request):
    version = request.headers.get(VERSION, '')
    version_by_date = request.headers.get(VERSION_BY_DATE, '')
    version_invalid = False
    if version and (not version.isdigit() or int(version) < 1):
        version_invalid = True
    if version_by_date and version_by_date != '':
        try:
            parse_date(version_by_date)
        except:
            if version_invalid or version == '':
                return404(request, 'header', 'version')
            else:
                request.validated[VERSION] = version
                request.validated[HASH] = request.headers.get(HASH, '')
                request.validated[VERSION_BY_DATE] = False
                return
    if version_invalid and version_by_date == '':
        return404(request, 'header', 'version')
    request.validated[VERSION] = version
    request.validated[HASH] = request.headers.get(HASH, '')
    request.validated[VERSION_BY_DATE] = request.headers.get(VERSION_BY_DATE, '')


def validate_accreditation(request):
    if request.authenticated_role != 'Administrator' and not request.check_accreditation(ACCREDITATION_LEVEL):
        request.errors.add('historical',
                           'accreditation',
                           'Broker Accreditation level does not '
                           'permit viewing tender historica info')
        request.errors.status = 403
        return


class HasRequestMethod(object):

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'HasRequestMethod = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        return hasattr(request, self.val)


class APIHistoricalResource(APIResource):

    def __init__(self, request, context):
        super(APIHistoricalResource, self).__init__(request, context)
        self.resource = request.context.doc_type.lower()

    @json_view(permission="view_historical",
               validators=(validate_accreditation, ))
    def get(self):
        route = get_route(self.request)
        if route is None:
            return404(self.request, 'url', '{}_id'.format(self.resource))
        msg = 'Request for {doc} {id} revision {ver} revision {rev}'.format(
            doc=self.resource, id=self.context.id,
            ver=self.request.validated[VERSION],
            rev=self.context.rev
        )

        self.LOGGER.info(msg, extra=context_unpack(self.request, {
            'MESSAGE_ID': '{}_historical'.format(self.resource)}))
        return call_view(self.request, self.context, route)
