import json
from datetime import datetime, timedelta
from typing import Any, Dict, Literal, Optional

from aiohttp.pytest_plugin import AiohttpClient
from freezegun import freeze_time

from openprocurement.violation_report.database.schema.violation_report import (
    ViolationReportReason,
)
from openprocurement.violation_report.tests.conftest import (
    api,
    event_loop,
    generate_doc_service_url,
    sub_app,
)
from openprocurement.violation_report.tests.factories.contract import ContractFactory

BROKER = "broker"

class TestFails:

    TARGET_DIR = 'docs/source/violation-reports/http/'

    async def request_to_http(
        self,
        api: AiohttpClient,
        filename: str,
        method: Literal["post", "put", "get", "patch", "delete"],
        url: str,
        headers: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ):
        # Request
        request_headers = []
        if headers is not None:
            for key, value in headers.items():
                request_headers.append(f"{key}: {value}")
        request_headers_text = "\n".join(request_headers)

        request_body = ""
        if json_data is not None:
            request_body = json.dumps(json_data, ensure_ascii=False, indent=2)

        # Response
        response = await getattr(api, method.lower())(
            url,
            headers=headers,
            json=json_data,
        )

        status_line = f"HTTP/1.0 {response.status} {response.reason}"
        response_headers = "\n".join(
            f"{k}: {v}"
            for k, v in response.headers.items()
            if k not in ("Date", "Server")
        )

        response_text = await response.text()
        try:
            parsed = json.loads(response_text)
            response_text = json.dumps(parsed, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            pass

        # Write to file
        with open(self.TARGET_DIR + filename, "w", encoding="utf-8") as f:
            f.write(f"{method.upper()} {url} HTTP/1.0\n")
            if request_headers_text:
                f.write(request_headers_text + "\n")
            f.write("\n")
            if request_body:
                f.write(request_body + "\n\n")
            f.write("\n")
            f.write(status_line + "\n")
            if response_headers:
                f.write(response_headers + "\n")
            f.write("\n")
            f.write(response_text)

        return response


    async def test_success(self, api, sub_app):
        now = datetime.fromisoformat("2025-10-12T15:35:35+03:00")
        with freeze_time(now):
            contract = await ContractFactory.create()
            resp = await self.request_to_http(
                api=api,
                filename="create-violation-report.http",
                method="post",
                url=f"/contracts/{contract.id}/violation_reports",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={"data": {
                    "reason": ViolationReportReason.signingRefusal,
                    "description": "Постачальник відмовився підписувати контракт.",
                    "documents": [
                        {
                            "title": "evidences.doc",
                            "url": generate_doc_service_url(sub_app),
                            "hash": "md5:" + "0" * 32,
                            "format": "application/msword",
                            "documentType": "violationReportEvidence",
                        },
                        {
                            "title": "sign.p7s",
                            "url": generate_doc_service_url(sub_app),
                            "hash": "md5:" + "0" * 32,
                            "format": "application/pkcs7-signature",
                            "documentType": "violationReportSignature",
                        }
                    ],
                }},
            )

            assert resp.status == 201, await resp.text()
            result = await resp.json()
            assert result["data"]["status"] == "pending"
            violation_report_id = result["data"]["id"]
            decision_period_start = result["data"]["decisionPeriod"]["startDate"]
            defendant_period_start = result["data"]["defendantPeriod"]["startDate"]

        # add response
        now = datetime.fromisoformat(defendant_period_start) + timedelta(hours=10, minutes=15)
        with freeze_time(now):
            resp = await self.request_to_http(
                api=api,
                filename="create-defendant-statement.http",
                method="put",
                url=f"/violation_reports/{violation_report_id}/defendantStatement",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={"data": {
                    "description": "В усьому винні бобри.",
                    "documents": [
                        {
                            "title": "beavers.gif",
                            "url": generate_doc_service_url(sub_app),
                            "hash": "md5:" + "0" * 32,
                            "format": "image/gif",
                            "documentType": "violationReportEvidence",
                        },
                        {
                            "title": "sign.p7s",
                            "url": generate_doc_service_url(sub_app),
                            "hash": "md5:" + "0" * 32,
                            "format": "application/pkcs7-signature",
                            "documentType": "violationReportSignature",
                        }
                    ],
                }},
            )
            assert resp.status == 201, await resp.text()

        # post decision
        now = datetime.fromisoformat(decision_period_start) + timedelta(hours=10, minutes=15)
        with freeze_time(now):
            resp = await self.request_to_http(
                api=api,
                filename="create-decision.http",
                method="put",
                url=f"/violation_reports/{violation_report_id}/decision",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={"data": {
                    "status": "declinedNoViolation",
                    "description": "Суворо засуджуємо бобрів.",
                    "documents": [
                        {
                            "title": "sign.p7s",
                            "url": generate_doc_service_url(sub_app),
                            "hash": "md5:" + "0" * 32,
                            "format": "application/pkcs7-signature",
                            "documentType": "violationReportSignature",
                        }
                    ],
                }},
            )
            assert resp.status == 201, await resp.text()


        # get violation report
        resp = await self.request_to_http(
            api=api,
            filename="get-violation-report.http",
            method="get",
            url=f"/violation_reports/{violation_report_id}",
        )
        assert resp.status == 200, await resp.text()
