from prozorro_cdb.violation_report.database.schema.violation_report import (
    ViolationReportReason,
)
from tests.base import BROKER_AUTH
from tests.factories.contract import ContractFactory


class TestFails:
    async def test_unauthorized(self, api):
        contract = await ContractFactory.create()

        resp = await api.post(f"/contracts/{contract.id}/violation_reports", json={})
        assert resp.status == 401, await resp.text()

    async def test_empty_request(self, api):
        contract = await ContractFactory.create()

        resp = await api.post(
            f"/contracts/{contract.id}/violation_reports",
            auth=BROKER_AUTH,
            json={},
        )
        assert resp.status == 400, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "data-validation",
            "title": "Data Validation Error",
            "details": "Validation errors in body",
            "status": 400,
            "errors": [{"type": "missing", "loc": ["data"], "msg": "Field required", "input": {}}],
        }

    async def test_contract_not_found(self, api):
        resp = await api.post(
            f"/contracts/{'a' * 32}/violation_reports",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "details": {
                        "reason": ViolationReportReason.signingRefusal,
                        "description": "",
                    }
                }
            },
        )
        assert resp.status == 404, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-not-found",
            "title": "Not Found",
            "details": "Contract not found.",
            "status": 404,
        }
