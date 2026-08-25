from datetime import datetime
from http import HTTPStatus

import pytest

from prozorro_cdb.api.database.schema.common import Period

from ..base import BROKER_AUTH
from ..conftest import generate_test_doc_url

# defendantPeriod that has already ended - decisions can be created/updated without extra time control
PAST_PERIOD = Period(
    startDate=datetime.fromisoformat("2020-01-01T00:00:00+02:00"),
    endDate=datetime.fromisoformat("2020-01-10T00:00:00+02:00"),
)

# defendantPeriod that is currently open, paired with a "now" that falls inside it
ACTIVE_PERIOD = Period(
    startDate=datetime.fromisoformat("2024-01-01T00:00:00+02:00"),
    endDate=datetime.fromisoformat("2024-01-10T00:00:00+02:00"),
)
NOW_IN_PERIOD = datetime.fromisoformat("2024-01-05T00:00:00+02:00")


@pytest.fixture
def signature_payload(sub_app):
    def _make(doc_hash="0" * 32):
        return {
            "title": "sign.p7s",
            "url": generate_test_doc_url(sub_app, doc_hash=doc_hash),
            "hash": "md5:" + doc_hash,
            "format": "application/pkcs7-signature",
            "documentType": "violationReportSignature",
        }

    return _make


@pytest.fixture
def create_decision(api):
    async def _create(violation_report_id, resolution="satisfied", description="рішення"):
        resp = await api.post(
            f"/violation_reports/{violation_report_id}/decisions",
            auth=BROKER_AUTH,
            json={"data": {"resolution": resolution, "description": description, "documents": []}},
        )
        assert resp.status == HTTPStatus.CREATED, await resp.text()
        return (await resp.json())["data"]["id"]

    return _create


@pytest.fixture
def publish_decision(api, sub_app, signature_payload):
    async def _publish(violation_report_id, decision_id):
        resp = await api.post(
            f"/violation_reports/{violation_report_id}/decisions/{decision_id}/documents",
            auth=BROKER_AUTH,
            json={"data": signature_payload()},
        )
        assert resp.status == HTTPStatus.CREATED, await resp.text()

        resp = await api.patch(
            f"/violation_reports/{violation_report_id}/decisions/{decision_id}",
            auth=BROKER_AUTH,
            json={"data": {"status": "active"}},
        )
        assert resp.status == HTTPStatus.OK, await resp.text()

    return _publish


@pytest.fixture
def create_statement(api):
    async def _create(violation_report_id, description="контраргументи"):
        resp = await api.post(
            f"/violation_reports/{violation_report_id}/defendantStatements",
            auth=BROKER_AUTH,
            json={"data": {"description": description, "documents": []}},
        )
        assert resp.status == HTTPStatus.CREATED, await resp.text()
        return (await resp.json())["data"]["id"]

    return _create


@pytest.fixture
def publish_statement(api):
    async def _publish(violation_report_id, statement_id):
        resp = await api.patch(
            f"/violation_reports/{violation_report_id}/defendantStatements/{statement_id}",
            auth=BROKER_AUTH,
            json={"data": {"status": "active"}},
        )
        assert resp.status == HTTPStatus.OK, await resp.text()

    return _publish
