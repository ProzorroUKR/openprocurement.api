from http import HTTPStatus

from prozorro_cdb.violation_report.database.schema.violation_report import (
    ViolationReportReason,
    ViolationReportStatus,
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
        assert resp.status == HTTPStatus.UNAUTHORIZED, await resp.text()

    async def test_empty_request(self, api):
        contract = await ContractFactory.create()

        resp = await api.post(
            f"/contracts/{contract.id}/violation_reports",
            auth=BROKER_AUTH,
            json={},
        )
        assert resp.status == HTTPStatus.BAD_REQUEST, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "data-validation",
            "title": "Data Validation Error",
            "details": "Validation errors in body",
            "status": HTTPStatus.BAD_REQUEST,
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
        assert resp.status == HTTPStatus.NOT_FOUND, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-not-found",
            "title": "Not Found",
            "details": "Contract not found.",
            "status": HTTPStatus.NOT_FOUND,
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
        assert resp.status == HTTPStatus.OK, await resp.text()
        result = await resp.json()
        assert result["data"]["details"]["reason"] == ViolationReportReason.contractBreach

    async def test_more_than_one_signature_document(self, api, signature_payload):
        contract = await ContractFactory.create()
        tender = await TenderFactory.create(_id=contract.tender_id)
        await AgreementFactory.create(_id=tender.agreement.id)

        resp = await api.post(
            f"/contracts/{contract.id}/violation_reports",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "details": {
                        "reason": ViolationReportReason.contractBreach,
                        "description": "Постачальник порушив контракт.",
                        "documents": [signature_payload(), signature_payload(doc_hash="1" * 32)],
                    }
                }
            },
        )
        assert resp.status == HTTPStatus.BAD_REQUEST, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-bad-request",
            "title": "Bad Request",
            "details": "More than one signature document found.",
            "status": HTTPStatus.BAD_REQUEST,
        }

    async def test_tender_not_found(self, api):
        contract = await ContractFactory.create()

        resp = await api.post(
            f"/contracts/{contract.id}/violation_reports",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "details": {
                        "reason": ViolationReportReason.contractBreach,
                        "description": "Постачальник порушив контракт.",
                    }
                }
            },
        )
        assert resp.status == HTTPStatus.NOT_FOUND, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-not-found",
            "title": "Not Found",
            "details": "Tender not found.",
            "status": HTTPStatus.NOT_FOUND,
        }

    async def test_tender_not_pq(self, api):
        contract = await ContractFactory.create()
        await TenderFactory.create(_id=contract.tender_id, procurementMethodType="belowThreshold")

        resp = await api.post(
            f"/contracts/{contract.id}/violation_reports",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "details": {
                        "reason": ViolationReportReason.contractBreach,
                        "description": "Постачальник порушив контракт.",
                    }
                }
            },
        )
        assert resp.status == HTTPStatus.BAD_REQUEST, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-bad-request",
            "title": "Bad Request",
            "details": "priceQuotation procedure expected.",
            "status": HTTPStatus.BAD_REQUEST,
        }

    async def test_agreement_not_found(self, api):
        contract = await ContractFactory.create()
        await TenderFactory.create(_id=contract.tender_id)

        resp = await api.post(
            f"/contracts/{contract.id}/violation_reports",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "details": {
                        "reason": ViolationReportReason.contractBreach,
                        "description": "Постачальник порушив контракт.",
                    }
                }
            },
        )
        assert resp.status == HTTPStatus.NOT_FOUND, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-not-found",
            "title": "Not Found",
            "details": "Agreement not found.",
            "status": HTTPStatus.NOT_FOUND,
        }


class TestPublish:
    async def test_publish_without_evidence_document(self, api):
        contract = await ContractFactory.create()
        tender = await TenderFactory.create(_id=contract.tender_id)
        await AgreementFactory.create(_id=tender.agreement.id)

        violation_report = await ViolationReportDBModelFactory.create(
            tender_id=tender.id,
            contract_id=contract.id,
            status=ViolationReportStatus.draft,
            details=ReportDetailsFactory.build(documents=[]),
        )

        resp = await api.patch(
            f"/violation_reports/{violation_report.id}",
            auth=BROKER_AUTH,
            json={"data": {"status": "pending"}},
        )
        assert resp.status == HTTPStatus.BAD_REQUEST, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-bad-request",
            "title": "Bad Request",
            "details": "Evidence document not found.",
            "status": HTTPStatus.BAD_REQUEST,
        }

    async def test_patch_details_forbidden_after_publish(self, api):
        violation_report = await ViolationReportDBModelFactory.create(
            status=ViolationReportStatus.pending,
        )

        resp = await api.patch(
            f"/violation_reports/{violation_report.id}",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "details": {
                        "reason": ViolationReportReason.contractBreach,
                        "description": "новий опис",
                    }
                }
            },
        )
        assert resp.status == HTTPStatus.BAD_REQUEST, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-bad-request",
            "title": "Bad Request",
            "details": "Details update forbidden in 'pending' status",
            "status": HTTPStatus.BAD_REQUEST,
        }


class TestListing:
    async def test_list_by_contract(self, api):
        contract = await ContractFactory.create()
        other_contract = await ContractFactory.create(tender_id=contract.tender_id)

        violation_report = await ViolationReportDBModelFactory.create(
            tender_id=contract.tender_id,
            contract_id=contract.id,
        )
        await ViolationReportDBModelFactory.create(
            tender_id=contract.tender_id,
            contract_id=other_contract.id,
        )

        resp = await api.get(f"/contracts/{contract.id}/violation_reports")
        assert resp.status == HTTPStatus.OK, await resp.text()
        result = await resp.json()
        assert [d["id"] for d in result["data"]] == [violation_report.id]

    async def test_list_by_contract_not_found(self, api):
        resp = await api.get(f"/contracts/{'a' * 32}/violation_reports")
        assert resp.status == HTTPStatus.NOT_FOUND, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-not-found",
            "title": "Not Found",
            "details": "Contract not found.",
            "status": HTTPStatus.NOT_FOUND,
        }

    async def test_list_by_tender(self, api):
        tender = await TenderFactory.create()
        other_tender = await TenderFactory.create()

        violation_report = await ViolationReportDBModelFactory.create(tender_id=tender.id)
        await ViolationReportDBModelFactory.create(tender_id=other_tender.id)

        resp = await api.get(f"/tender/{tender.id}/violation_reports")
        assert resp.status == HTTPStatus.OK, await resp.text()
        result = await resp.json()
        assert [d["id"] for d in result["data"]] == [violation_report.id]
