from openprocurement.api.context import set_now
from json import loads
import os.path
from openprocurement.api.tests.base import singleton_app, app


def get_fixture_json(name):
    current_dir = os.path.dirname(__file__)
    fixture_file = os.path.join(current_dir, "data", f"{name}.json")
    with open(fixture_file) as f:
        data = loads(f.read())
    return data


def test_render_tender(app):
    response = app.get("/tenders/520d3c3a9a9f47b9bec63eb6d86610eb", status=404)

    data = get_fixture_json("tender_to_render")
    set_now()
    app.app.registry.mongodb.tenders.save(data, insert=True)

    response = app.get("/render/txt/tenders/520d3c3a9a9f47b9bec63eb6d86610eb")
    print(response.body)
    print(response.text)
    print(response.status_code)


