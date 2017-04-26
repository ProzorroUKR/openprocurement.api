from openprocurement.api.utils import (
    error_handler,
    _apply_patch,
)
from jsonpointer import JsonPointerException
from jsonpatch import JsonPatchException

from pyramid.interfaces import IRouteRequest, IRoutesMapper
from zope.interface import providedBy

from pyramid.view import _call_view
from openprocurement.historical.core.constants import (
    HASH, VERSION, PREVIOUS_HASH as PHASH
)


def extract_doc(request, doc_type):
    doc_id = request.matchdict['doc_id']
    if doc_id is None:
        return404(request, 'url', '{}_id'.format(doc_type.lower()))

    doc = request.registry.db.get(request.matchdict['doc_id'])
    if doc is None or doc.get('doc_type') != doc_type:
        return404(request, 'url', '{}_id'.format(doc_type.lower()))

    revisions = doc.pop('revisions', [])
    if not revisions:
        add_responce_headers(request, '0', '')
        return doc

    current_version = len(revisions)
    current_hash = parse_hash(revisions[-1].get('rev', ''))

    header, rev = extract_header(request)
    if header == 0 or header > len(revisions):
        add_responce_headers(request, current_version, current_hash)
        add_prev_hash_header(request, revisions, current_version - 1)
        return doc
    doc, parsed_hash = apply_while(doc, header, revisions)
    if not rev:
        rev = parsed_hash

    if not doc or rev != parsed_hash:
        return404(request, 'header', 'hash')
    add_responce_headers(request, header, parsed_hash)
    add_prev_hash_header(request, revisions, header)
    return doc


def add_prev_hash_header(request, revisions, version):
    _hash = str(revisions[version - 1].get('rev', ''))
    headers = request.response.headerlist
    if _hash:
        headers.append((PHASH, parse_hash(_hash)))
    else:
        headers.append((PHASH, ''))


def extract_header(request):
    version = request.headers.get(VERSION, '')
    _hash = request.headers.get(HASH, '')
    if not version:
        return 0, _hash
    if not version.isdigit():
        return404(request, 'header', 'version')
    return int(version), _hash


def add_responce_headers(request, version, _hash=''):
    if not isinstance(version, str):
        version = str(version)
    if not isinstance(_hash, str):
        _hash = str(_hash)

    request.response.headerlist.append((VERSION, version))
    request.response.headerlist.append((HASH, _hash))


def apply_while(doc, header, revisions):
    for version, patch in reversed(list(enumerate(revisions))):
        try:
            doc = _apply_patch(doc, patch['changes'])
        except (JsonPointerException, JsonPatchException):
            return {}, ''
        if version == header:
            doc['dateModified'] = find_dateModified(revisions[:version+1])
            return doc, parse_hash(patch['rev'])
    return {}, ''


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


class HasRequestMethod(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'HasRequestMethod = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        return hasattr(request, self.val)
