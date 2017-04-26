from jsonpointer import JsonPointerException
from jsonpatch import JsonPatchException
from pyramid.interfaces import IRouteRequest, IRoutesMapper
from zope.interface import providedBy
from pyramid.view import _call_view
from pyramid.security import Allow
from openprocurement.historical.core.constants import (
    VERSION, HASH, PREVIOUS_HASH
)
from openprocurement.api.utils import (
    error_handler,
    _apply_patch,
    APIResource,
    json_view,
)


class Root(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
        (Allow, 'g:historical', 'view_historical')
    ]

    def __init__(self, request):
        self.request = request
        self.db = request.registry.db


def extract_doc(request, doc_type):
    doc_id = request.matchdict['doc_id']
    if doc_id is None:
        return404(request, 'url', '{}_id'.format(doc_type.lower()))

    doc = request.registry.db.get(doc_id)
    if doc is None or doc.get('doc_type') != doc_type:
        return404(request, 'url', '{}_id'.format(doc_type.lower()))

    doc, revision_hash, prev_hash = apply_while(request, doc)
    add_responce_headers(request, rhash=revision_hash, phash=prev_hash)
    return doc


def add_responce_headers(request, version='', rhash='', phash=''):
    add = request.response.headerlist.append
    add((VERSION, str(version) or request.validated['historical_header_version']))
    add((HASH, rhash))
    if phash:
        add((PREVIOUS_HASH, phash))


def raise_not_implemented(request):
    request.errors.status = 501
    request.errors.add('tender', 'revision', 'Not Implemented')
    raise error_handler(request.errors)


def apply_while(request, doc):
    revisions = doc.pop('revisions', [])
    if not revisions:
        add_responce_headers(request, '0', '')
        return doc, parse_hash(doc.get('rev')), ''

    for version, patch in reversed(list(enumerate(revisions))):
        try:
            doc = _apply_patch(doc, patch['changes'])
        except (JsonPointerException, JsonPatchException):
            raise_not_implemented(request)
        if version == request.validated['historical_header_version']:

            if request.validated['historical_header_hash'] and\
               request.validated['historical_header_hash'] != parse_hash(patch.get('rev')):
                return404('header', 'hash')

            doc['dateModified'] = find_dateModified(revisions[:version+1])
            return (doc,
                    parse_hash(patch['rev']),
                    parse_hash(revisions[version - 1].get('rev', '')))
    return {}, '', ''


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
                continue
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
    if rev_hash:
        return rev_hash.split('-')[1]
    return ''


def validate_header(request):
    version = request.headers.get(VERSION, '')
    if not version or not version.isdigit():
        request.errors.status = 404
        request.errors.add('header', 'version', 'Not Found')
        return
    request.validated['historical_header_version'] = int(version)
    request.validated['historical_header_hash'] = request.headers.get(HASH, '')


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

    @json_view(permission="view_historical", validators=(validate_header,))
    def get(self):
        route = get_route(self.request)
        if route is None:
            return404(self.request, 'url', '{}_id'.format(self.resource))
        return call_view(self.request, self.context, route)
