from datetime import datetime, timedelta
from http import HTTPStatus

from freezegun import freeze_time

from ..base import BROKER_AUTH
from ..factories.violation_report import ViolationReportDBModelFactory
from .conftest import PAST_PERIOD


class TestCreateDecision:
    async def test_forbidden_while_another_is_active(self, api, sub_app, create_decision, publish_decision):
        violation_report = await ViolationReportDBModelFactory.create(defendantPeriod=PAST_PERIOD)

        decision_id = await create_decision(violation_report.id)
        await publish_decision(violation_report.id, decision_id)

        resp = await api.post(
            f"/violation_reports/{violation_report.id}/decisions",
            auth=BROKER_AUTH,
            json={"data": {"resolution": "satisfied", "description": "друге рішення", "documents": []}},
        )
        assert resp.status == HTTPStatus.BAD_REQUEST, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-bad-request",
            "title": "Bad Request",
            "details": "Decision is active.",
            "status": HTTPStatus.BAD_REQUEST,
        }


class TestUpdateDecision:
    async def test_forbidden_while_another_is_active(self, api, sub_app, create_decision, publish_decision):
        violation_report = await ViolationReportDBModelFactory.create(defendantPeriod=PAST_PERIOD)

        active_decision_id = await create_decision(violation_report.id, description="перше рішення")
        draft_decision_id = await create_decision(violation_report.id, description="друге рішення")
        await publish_decision(violation_report.id, active_decision_id)

        # editing an unrelated draft decision is blocked once another one is active
        resp = await api.patch(
            f"/violation_reports/{violation_report.id}/decisions/{draft_decision_id}",
            auth=BROKER_AUTH,
            json={"data": {"resolution": "satisfied", "description": "оновлення"}},
        )
        assert resp.status == HTTPStatus.BAD_REQUEST, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-bad-request",
            "title": "Bad Request",
            "details": "Decision is active.",
            "status": HTTPStatus.BAD_REQUEST,
        }

    async def test_post_duplicate_signature(self, api, create_decision, signature_payload):
        violation_report = await ViolationReportDBModelFactory.create(defendantPeriod=PAST_PERIOD)
        decision_id = await create_decision(violation_report.id)

        resp = await api.post(
            f"/violation_reports/{violation_report.id}/decisions/{decision_id}/documents",
            auth=BROKER_AUTH,
            json={"data": signature_payload()},
        )
        assert resp.status == HTTPStatus.CREATED, await resp.text()

        resp = await api.post(
            f"/violation_reports/{violation_report.id}/decisions/{decision_id}/documents",
            auth=BROKER_AUTH,
            json={"data": signature_payload(doc_hash="1" * 32)},
        )
        assert resp.status == HTTPStatus.BAD_REQUEST, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-bad-request",
            "title": "Bad Request",
            "details": "Signature document already exists. Update it with PUT method instead.",
            "status": HTTPStatus.BAD_REQUEST,
        }


class TestPublishDecision:
    async def test_publish_without_signature(self, api, create_decision):
        violation_report = await ViolationReportDBModelFactory.create(defendantPeriod=PAST_PERIOD)
        decision_id = await create_decision(violation_report.id)

        resp = await api.patch(
            f"/violation_reports/{violation_report.id}/decisions/{decision_id}",
            auth=BROKER_AUTH,
            json={"data": {"status": "active"}},
        )
        assert resp.status == HTTPStatus.BAD_REQUEST, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-bad-request",
            "title": "Bad Request",
            "details": "Signature document not found.",
            "status": HTTPStatus.BAD_REQUEST,
        }

    async def test_publish_with_stale_signature(self, api, create_decision, signature_payload):
        t0 = datetime.fromisoformat("2024-01-01T10:00:00+02:00")
        with freeze_time(t0):
            violation_report = await ViolationReportDBModelFactory.create(defendantPeriod=PAST_PERIOD)
            decision_id = await create_decision(violation_report.id)

            resp = await api.post(
                f"/violation_reports/{violation_report.id}/decisions/{decision_id}/documents",
                auth=BROKER_AUTH,
                json={"data": signature_payload()},
            )
            assert resp.status == HTTPStatus.CREATED, await resp.text()

        # decision gets updated after the signature was uploaded
        with freeze_time(t0 + timedelta(minutes=5)):
            resp = await api.patch(
                f"/violation_reports/{violation_report.id}/decisions/{decision_id}",
                auth=BROKER_AUTH,
                json={"data": {"resolution": "satisfied", "description": "оновлене рішення"}},
            )
            assert resp.status == HTTPStatus.OK, await resp.text()

        with freeze_time(t0 + timedelta(minutes=10)):
            resp = await api.patch(
                f"/violation_reports/{violation_report.id}/decisions/{decision_id}",
                auth=BROKER_AUTH,
                json={"data": {"status": "active"}},
            )
            assert resp.status == HTTPStatus.BAD_REQUEST, await resp.text()
            result = await resp.json()
            assert result == {
                "type": "http-bad-request",
                "title": "Bad Request",
                "details": "Signature document should be updated.",
                "status": HTTPStatus.BAD_REQUEST,
            }


class TestDecisionListView:
    async def test_hides_draft_shows_active(self, api, sub_app, create_decision, publish_decision):
        violation_report = await ViolationReportDBModelFactory.create(defendantPeriod=PAST_PERIOD)
        decision_id = await create_decision(violation_report.id)

        resp = await api.get(f"/violation_reports/{violation_report.id}/decisions")
        assert resp.status == HTTPStatus.OK, await resp.text()
        assert (await resp.json())["data"] == []

        await publish_decision(violation_report.id, decision_id)

        resp = await api.get(f"/violation_reports/{violation_report.id}/decisions")
        assert resp.status == HTTPStatus.OK, await resp.text()
        result = await resp.json()
        assert [d["id"] for d in result["data"]] == [decision_id]
