import os.path
import json
from cornice.resource import resource
from copy import deepcopy
from uuid import uuid4
from openprocurement.historical.core.utils import Root, APIHistoricalResource, json_view


here = os.path.dirname(__file__)
with open(os.path.join(here, "data.json")) as in_json:
    test_data_with_revisions = json.load(in_json)


class Doc(dict):
    __parent__ = None
    doc_type = "mock"
    hash = (uuid4().hex,)
    id = test_data_with_revisions["id"]
    rev = test_data_with_revisions["_rev"]

    def __init___(self, *args, **kwargs):
        super(Doc, self).__init__(*args, **kwargs)


mock_doc = Doc(test_data_with_revisions)


class Db(dict):
    save = dict.__setitem__

    def __init__(self, *args, **kwargs):
        super(Db, self).__init__(*args, **kwargs)
        self[mock_doc.id] = deepcopy(mock_doc)
        broken = deepcopy(mock_doc)
        broken["revisions"][:] = [
            {"changes": [{"path": "/invalid/path", "op": "remove"}], "rev": uuid4()} for _ in range(10)
        ]
        self["broken"] = deepcopy(broken)

    def get(self, key):
        if key in self:
            return deepcopy(self[key])

    def __getattr__(self, item):
        # print(f"getting collection {item}")
        return self


def dummy_factory(request):
    root = Root(request)
    doc = request.extract_doc_versioned("mock")
    if not request.matchdict or not request.matchdict.get("doc_id"):
        return root
    request.validated["mock_id"] = request.matchdict["doc_id"]
    doc.__parent__ = root
    request.validated["mock"] = request.validated["db_doc"] = doc
    return doc


def cornice_factory(request):
    root = Root(request)
    doc = deepcopy(mock_doc)
    if not request.matchdict or not request.matchdict.get("doc_id"):
        return root
    request.validated["mock_id"] = request.matchdict["doc_id"]
    doc.__parent__ = root
    request.validated["mock"] = request.validated["db_doc"] = doc
    return doc


@resource(name="MockBase", path="/mock/{doc_id}", factory=cornice_factory)
class DummyBaseResource(APIHistoricalResource):
    @json_view()
    def get(self):
        self.context.update({"Base": "OK!"})
        return self.context


@resource(name="MockHistorical", path="/mock/{doc_id}/historical", factory=dummy_factory)
class DummyHistoricalResource(APIHistoricalResource):
    pass
