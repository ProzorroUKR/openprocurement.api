# -*- coding: utf-8 -*-
from datetime import timedelta
from openprocurement.api.tests.base import singleton_app, app
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.tests.utils import change_auth

fake_tender_data = {
    "doc_type": "Tender",
    "_id": "Fake_tender_id",
    "revisions": [{"date": (RELEASE_2020_04_19 + timedelta(days=1)).isoformat()}],
    "dateCreated": (RELEASE_2020_04_19 + timedelta(days=1)).isoformat()
}

fake_complaint_data = {
    "id": "Fake_complaint_id",
    "status": "Fake_status",
    "author": "Fake_author",
    "complaintID": "Fake_pretty_complaint_id",
    "owner_token": "Fake_owner_token",
    "type": "complaint"
}

fake_invalid_complaint_data = {
    "id": "Fake_invalid_complaint_id",
    "status": "Fake_invalid_status",
    "author": "Fake_invalid_author",
    "complaintID": "Fake_invalid_pretty_complaint_id",
    "owner_token": "Fake_invalid_owner_token",
    "type": "complaint"
}

fake_tender_complaint_data = {
    "complaints": [fake_invalid_complaint_data, fake_complaint_data],
    "tags": [{"name": "alf"}, {"name": "bet"}]
}
fake_qualification_complaint_data = {
    "qualifications": [{
        "id": "Fake_qualification_id",
        "complaints": [fake_invalid_complaint_data, fake_complaint_data]
    }]
}
fake_award_complaint_data = {
    "awards": [{
        "id": "Fake_award_id",
        "complaints": [fake_invalid_complaint_data, fake_complaint_data]
    }]
}
fake_cancellation_complaint_data = {
    "cancellations": [{
        "id": "Fake_cancellation_id",
        "complaints": [fake_invalid_complaint_data, fake_complaint_data]
    }]
}


def save_fake_tender_data(app, data=None):
    tender_data = fake_tender_data.copy()
    if data:
        tender_data.update(data)

    filters = {}
    uid = tender_data.pop("_id", None)
    if uid:
        filters["_id"] = uid
    app.app.registry.mongodb.tenders.collection.update_one(
        filters,
        {"$set": tender_data},
        upsert=True,
    )
    return tender_data


def assert_complaint_data(response):
    assert response.status_code == 200
    assert len(response.json["data"]) == 1
    assert response.json["data"][0]["access"]["token"] == "Fake_owner_token"
    assert response.json["data"][0]["params"]["tender_id"] == "Fake_tender_id"
    assert response.json["data"][0]["params"]["complaint_id"] == "Fake_complaint_id"


def search_complaint(app, query=None, auth=("Basic", ("bot", "bot")), status=200):
    url = "/complaints/search"
    if query:
        url = "{}?{}".format(url, query)
    with change_auth(app, auth):
        response = app.get(url, status=status)
    assert response.status_code == status
    return response


def test_search_complaint_forbidden(app):
    save_fake_tender_data(app)
    response = search_complaint(app, query="complaint_id=Fake_pretty_complaint_id", auth=None, status=403)
    assert response.status_code == 403


def test_search_complaint_no_query(app):
    save_fake_tender_data(app)
    response = search_complaint(app)
    assert len(response.json["data"]) == 0


def test_search_complaint_invalid_query(app):
    save_fake_tender_data(app)
    response = search_complaint(app)
    assert len(response.json["data"]) == 0


def test_search_complaint_not_found(app):
    save_fake_tender_data(app)
    response = search_complaint(app, query="some_param=some_id")
    assert len(response.json["data"]) == 0


def test_search_tender_complaint_by_payment_id(app):
    save_fake_tender_data(app, fake_tender_complaint_data)
    response = search_complaint(app, query="complaint_id=Fake_pretty_complaint_id")
    assert_complaint_data(response)
    assert response.json["data"][0]["params"]["item_type"] is None
    assert response.json["data"][0]["params"]["item_id"] is None


def test_search_qualification_complaint_by_payment_id(app):
    save_fake_tender_data(app, fake_qualification_complaint_data)
    response = search_complaint(app, query="complaint_id=Fake_pretty_complaint_id")
    assert_complaint_data(response)
    assert response.json["data"][0]["params"]["item_type"] == "qualifications"
    assert response.json["data"][0]["params"]["item_id"] == "Fake_qualification_id"


def test_search_award_complaint_by_payment_id(app):
    save_fake_tender_data(app, fake_award_complaint_data)
    response = search_complaint(app, query="complaint_id=Fake_pretty_complaint_id")
    assert_complaint_data(response)
    assert response.json["data"][0]["params"]["item_type"] == "awards"
    assert response.json["data"][0]["params"]["item_id"] == "Fake_award_id"


def test_search_cancellation_complaint_by_payment_id(app):
    save_fake_tender_data(app, fake_cancellation_complaint_data)
    response = search_complaint(app, query="complaint_id=Fake_pretty_complaint_id")
    assert_complaint_data(response)
    assert response.json["data"][0]["params"]["item_type"] == "cancellations"
    assert response.json["data"][0]["params"]["item_id"] == "Fake_cancellation_id"
