from openprocurement.api.tests.base import singleton_app, app
from openprocurement.api.context import set_now
from json import loads
import os.path
import difflib


def get_fixture(name, ext="json"):
    current_dir = os.path.dirname(__file__)
    fixture_file = os.path.join(current_dir, "data", f"{name}.{ext}")
    with open(fixture_file) as f:
        data = f.read()
        if ext == "json":
            data = loads(data)
    return data


def test_render_tender(app):
    data = get_fixture("tender_to_render", ext="json")
    set_now()
    app.app.registry.mongodb.tenders.save(data, insert=True)

    response = app.get("/render/txt/tenders/520d3c3a9a9f47b9bec63eb6d86610eb")
    expected = get_fixture("tender_to_render", ext="txt")
    # diff = difflib.ndiff(expected.splitlines(keepends=True),
    #                      response.text.splitlines(keepends=True))
    # print(''.join(diff), end="")
    assert expected == response.text
