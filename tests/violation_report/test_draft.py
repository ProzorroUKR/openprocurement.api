from prozorro_cdb.violation_report.database.schema.violation_report import (
    ViolationReportReason,
)

from ..base import BROKER_AUTH
from ..factories.agreement import AgreementFactory
from ..factories.contract import ContractFactory
from ..factories.tender import TenderFactory
from ..factories.violation_report import (
    ReportDetailsFactory,
    ViolationReportDBModelFactory,
)


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

    async def test_patch_reason(self, api):
        contract = await ContractFactory.create()
        tender = await TenderFactory.create(_id=contract.tender_id)
        await AgreementFactory.create(_id=tender.agreement.id)

        violation_report = await ViolationReportDBModelFactory.create(
            tender_id=tender.id,
            contract_id=contract.id,
            details=ReportDetailsFactory.build(
                reason=ViolationReportReason.goodsNonCompliance,
            ),
        )

        resp = await api.patch(
            f"/violation_reports/{violation_report.id}",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "details": {
                        "reason": ViolationReportReason.contractBreach,
                        "description": violation_report.details.description,
                    }
                }
            },
        )
        assert resp.status == 200, await resp.text()
        result = await resp.json()
        assert result["data"]["details"]["reason"] == ViolationReportReason.contractBreach
