from datetime import datetime, timedelta

from freezegun import freeze_time

from openprocurement.violation_report.database.schema.violation_report import (
    ViolationReportReason,
)
from openprocurement.violation_report.tests.conftest import (
    generate_doc_service_url,
    sub_app,
)
from openprocurement.violation_report.tests.factories.agreement import AgreementFactory
from openprocurement.violation_report.tests.factories.contract import ContractFactory
from openprocurement.violation_report.tests.factories.tender import TenderFactory

from .conftest import request_to_http
from .constants import BROKER

TARGET_DIR = 'docs/source/violation-reports/http/'


class TestFails:

    async def test_success(self, request_to_http, sub_app):
        now = datetime.fromisoformat("2025-10-12T15:35:35+03:00")
        with freeze_time(now):
            contract = await ContractFactory.create()
            tender = await TenderFactory.create(_id=contract.tender_id)
            await AgreementFactory.create(_id=tender.agreement.id)

            resp = await request_to_http(
                filename=TARGET_DIR + "01-create-violation-report-draft.http",
                method="post",
                url=f"/contracts/{contract.id}/violation_reports",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={"data": {
                    "details": {
                        "reason": ViolationReportReason.signingRefusal,
                        "description": "Постачальник відмовився підписувати контракт.",
                        "documents": [
                            {
                                "title": "evidences.doc",
                                "url": generate_doc_service_url(sub_app),
                                "hash": "md5:" + "0" * 32,
                                "format": "application/msword",
                                "documentType": "violationReportEvidence",
                            }
                        ],
                    }
                }},
            )

            assert resp.status == 201, await resp.text()
            result = await resp.json()
            assert result["data"]["status"] == "draft"
            assert "defendantPeriod" not in result["data"]
            violation_report_id = result["data"]["id"]

        # add signature
        now += timedelta(seconds=120)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "02-post-violation-report-draft-signature.http",
                method="post",
                url=f"/violation_reports/{violation_report_id}/details/documents",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={"data": {
                    "title": "sign.p7s",
                    "url": generate_doc_service_url(sub_app),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pkcs7-signature",
                    "documentType": "violationReportSignature",
                }},
            )
            assert resp.status == 201, await resp.text()

        # publish report
        now += timedelta(seconds=35)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "03-publish-violation-report-draft.http",
                method="patch",
                url=f"/violation_reports/{violation_report_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={"data": {
                    "status": "pending",
                }},
            )
            assert resp.status == 200, await resp.text()
            result = await resp.json()
            defendant_period_start = result["data"]["defendantPeriod"]["startDate"]
            defendant_period_end = result["data"]["defendantPeriod"]["endDate"]

        # add response
        now = datetime.fromisoformat(defendant_period_start) + timedelta(hours=10, minutes=15)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "04-create-defendant-statement.http",
                method="put",
                url=f"/violation_reports/{violation_report_id}/defendantStatement",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={"data": {"description": "В усьому винні бобри."}},
            )
            assert resp.status == 201, await resp.text()

        # add response evidence document
        now += timedelta(seconds=15)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "05-add-defendant-statement-evidence.http",
                method="post",
                url=f"/violation_reports/{violation_report_id}/defendantStatement/documents",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={"data": {
                    "title": "beavers.gif",
                    "url": generate_doc_service_url(sub_app),
                    "hash": "md5:" + "0" * 32,
                    "format": "image/gif",
                    "documentType": "violationReportEvidence",
                }},
            )
            assert resp.status == 201, await resp.text()

        # add response signature
        now += timedelta(seconds=15)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "06-add-defendant-statement-signature.http",
                method="post",
                url=f"/violation_reports/{violation_report_id}/defendantStatement/documents",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={"data": {
                    "title": "sign.p7s",
                    "url": generate_doc_service_url(sub_app),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pkcs7-signature",
                    "documentType": "violationReportSignature",
                }},
            )
            assert resp.status == 201, await resp.text()

        # post decision
        now = datetime.fromisoformat(defendant_period_end) + timedelta(hours=10, minutes=15)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "07-create-decision.http",
                method="put",
                url=f"/violation_reports/{violation_report_id}/decision",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={"data": {
                    "status": "declinedNoViolation",
                    "description": "Суворо засуджуємо бобрів.",
                }},
            )
            assert resp.status == 201, await resp.text()

        # add decision signature
        now += timedelta(seconds=12)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "08-post-decision-signature.http",
                method="post",
                url=f"/violation_reports/{violation_report_id}/decision/documents",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={"data": {
                    "title": "sign.p7s",
                    "url": generate_doc_service_url(sub_app),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pkcs7-signature",
                    "documentType": "violationReportSignature",
                }},
            )
            assert resp.status == 201, await resp.text()

        # get violation report
        resp = await request_to_http(
            filename=TARGET_DIR + "09-get-violation-report.http",
            method="get",
            url=f"/violation_reports/{violation_report_id}",
        )
        assert resp.status == 200, await resp.text()
