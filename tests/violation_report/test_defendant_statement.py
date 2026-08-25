from http import HTTPStatus

from freezegun import freeze_time

from ..base import BROKER_AUTH
from ..factories.violation_report import ViolationReportDBModelFactory
from .conftest import ACTIVE_PERIOD, NOW_IN_PERIOD


class TestCreateDefendantStatement:
    async def test_forbidden_while_another_is_active(self, api, create_statement, publish_statement):
        with freeze_time(NOW_IN_PERIOD):
            violation_report = await ViolationReportDBModelFactory.create(defendantPeriod=ACTIVE_PERIOD)

            statement_id = await create_statement(violation_report.id)
            await publish_statement(violation_report.id, statement_id)

            resp = await api.post(
                f"/violation_reports/{violation_report.id}/defendantStatements",
                auth=BROKER_AUTH,
                json={"data": {"description": "друга заява", "documents": []}},
            )
            assert resp.status == HTTPStatus.BAD_REQUEST, await resp.text()
            result = await resp.json()
            assert result == {
                "type": "http-bad-request",
                "title": "Bad Request",
                "details": "Defendant statement is active.",
                "status": HTTPStatus.BAD_REQUEST,
            }


class TestUpdateDefendantStatement:
    async def test_forbidden_while_another_is_active(self, api, create_statement, publish_statement):
        with freeze_time(NOW_IN_PERIOD):
            violation_report = await ViolationReportDBModelFactory.create(defendantPeriod=ACTIVE_PERIOD)

            active_statement_id = await create_statement(violation_report.id, description="перша заява")
            draft_statement_id = await create_statement(violation_report.id, description="друга заява")
            await publish_statement(violation_report.id, active_statement_id)

            # editing an unrelated draft statement is blocked once another one is active
            resp = await api.patch(
                f"/violation_reports/{violation_report.id}/defendantStatements/{draft_statement_id}",
                auth=BROKER_AUTH,
                json={"data": {"description": "оновлення"}},
            )
            assert resp.status == HTTPStatus.BAD_REQUEST, await resp.text()
            result = await resp.json()
            assert result == {
                "type": "http-bad-request",
                "title": "Bad Request",
                "details": "Defendant statement is active.",
                "status": HTTPStatus.BAD_REQUEST,
            }

    async def test_post_duplicate_signature(self, api, create_statement, signature_payload):
        with freeze_time(NOW_IN_PERIOD):
            violation_report = await ViolationReportDBModelFactory.create(defendantPeriod=ACTIVE_PERIOD)
            statement_id = await create_statement(violation_report.id)

            resp = await api.post(
                f"/violation_reports/{violation_report.id}/defendantStatements/{statement_id}/documents",
                auth=BROKER_AUTH,
                json={"data": signature_payload()},
            )
            assert resp.status == HTTPStatus.CREATED, await resp.text()

            resp = await api.post(
                f"/violation_reports/{violation_report.id}/defendantStatements/{statement_id}/documents",
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


class TestDefendantStatementListView:
    async def test_hides_draft_shows_active(self, api, create_statement, publish_statement):
        with freeze_time(NOW_IN_PERIOD):
            violation_report = await ViolationReportDBModelFactory.create(defendantPeriod=ACTIVE_PERIOD)
            statement_id = await create_statement(violation_report.id)

            resp = await api.get(f"/violation_reports/{violation_report.id}/defendantStatements")
            assert resp.status == HTTPStatus.OK, await resp.text()
            assert (await resp.json())["data"] == []

            await publish_statement(violation_report.id, statement_id)

            resp = await api.get(f"/violation_reports/{violation_report.id}/defendantStatements")
            assert resp.status == HTTPStatus.OK, await resp.text()
            result = await resp.json()
            assert [d["id"] for d in result["data"]] == [statement_id]
