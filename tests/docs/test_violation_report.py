from datetime import datetime, timedelta
from unittest.mock import ANY

from freezegun import freeze_time

from prozorro_cdb.violation_report.database.schema.violation_report import (
    ViolationReportReason,
    ViolationReportStatus,
)

from ..conftest import generate_test_doc_url
from ..factories.agreement import AgreementFactory
from ..factories.contract import ContractFactory
from ..factories.tender import TenderFactory
from .constants import BROKER

TARGET_DIR = "docs/source/violation-reports/http/"


class TestViolationReport:
    async def test_success(self, deterministic_environment, request_to_http, sub_app):
        now = datetime.fromisoformat("2025-10-12T15:35:35+03:00")
        with freeze_time(now):
            contract = await ContractFactory.create()
            tender = await TenderFactory.create(_id=contract.tender_id)
            await AgreementFactory.create(_id=tender.agreement.id)

            resp = await request_to_http(
                filename=TARGET_DIR + "01-00-post-report-draft.http",
                method="post",
                url=f"/contracts/{contract.id}/violation_reports",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "details": {
                            "reason": ViolationReportReason.contractBreach,
                            "description": "Постачальник порушив контракт.",
                            "documents": [
                                {
                                    "title": "evidences.doc",
                                    "url": generate_test_doc_url(sub_app),
                                    "hash": "md5:" + "0" * 32,
                                    "format": "application/msword",
                                    "documentType": "violationReportEvidence",
                                }
                            ],
                        }
                    }
                },
            )

        assert resp.status == 201, await resp.text()
        result = await resp.json()
        assert result["data"]["status"] == "draft"
        assert "defendantPeriod" not in result["data"]
        violation_report_id = result["data"]["id"]
        evidence_doc_id = result["data"]["details"]["documents"][0]["id"]

        # update violation report
        now += timedelta(seconds=30)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "01-01-patch-report-draft.http",
                method="patch",
                url=f"/violation_reports/{violation_report_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "details": {
                            "reason": ViolationReportReason.goodsNonCompliance,
                            "description": "Якість товару не відповідає нормі.",
                        }
                    }
                },
            )
            assert resp.status == 200, await resp.text()

        # delete document
        now += timedelta(seconds=15)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "01-02-delete-document.http",
                method="delete",
                url=f"/violation_reports/{violation_report_id}/details/documents/{evidence_doc_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
            )
            assert resp.status == 204, await resp.text()

        # post another evidence doc
        now += timedelta(seconds=15)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "01-03-post-details-document.http",
                method="post",
                url=f"/violation_reports/{violation_report_id}/details/documents",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "title": "evidence_document_2.pdf",
                        "url": generate_test_doc_url(sub_app, doc_hash="a" * 32),
                        "hash": "md5:" + "a" * 32,
                        "format": "application/pdf",
                        "documentType": "violationReportEvidence",
                    }
                },
            )
            assert resp.status == 201, await resp.text()
            evidence_doc_id = (await resp.json())["data"]["id"]

        # update evidences doc
        now += timedelta(seconds=35)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "01-04-put-report-document-evidence.http",
                method="put",
                url=f"/violation_reports/{violation_report_id}/details/documents/{evidence_doc_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "title": "evidence_updated.pdf",
                        "url": generate_test_doc_url(sub_app, doc_hash="1" * 32),
                        "hash": "md5:" + "1" * 32,
                        "format": "application/pdf",
                        "documentType": "violationReportEvidence",
                    }
                },
            )
            assert resp.status == 201, await resp.text()

        # update evidences doc description
        now += timedelta(seconds=35)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "01-05-patch-report-document-evidence.http",
                method="patch",
                url=f"/violation_reports/{violation_report_id}/details/documents/{evidence_doc_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "title": "доказ_оновлений.pdf",
                        "title_en": "evidence_updated.pdf",
                        "description": "Висновок експерта, щодо пошкодженої деревини.",
                        "description_en": "Expert opinion regarding damaged wood.",
                    }
                },
            )
            assert resp.status == 200, await resp.text()

        # publish report
        now += timedelta(seconds=35)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "01-06-publish-report-draft.http",
                method="patch",
                url=f"/violation_reports/{violation_report_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "status": "pending",
                    }
                },
            )
            assert resp.status == 200, await resp.text()
            result = await resp.json()
            defendant_period_start = result["data"]["defendantPeriod"]["startDate"]
            defendant_period_end = result["data"]["defendantPeriod"]["endDate"]

        # --<<== Defendant Statement =>>=-- #
        now = datetime.fromisoformat(defendant_period_start) + timedelta(hours=10, minutes=15, seconds=12)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "02-01-put-defendant-statement.http",
                method="post",
                url=f"/violation_reports/{violation_report_id}/defendantStatements",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "description": "В усьому винні бобри.",
                        "documents": [
                            {
                                "title": "beavers.gif",
                                "url": generate_test_doc_url(sub_app),
                                "hash": "md5:" + "0" * 32,
                                "format": "image/gif",
                                "documentType": "violationReportEvidence",
                            }
                        ],
                    }
                },
            )
            assert resp.status == 201, await resp.text()
            defendant_statement = (await resp.json())["data"]
            defendant_statement_id = defendant_statement["id"]
            defendant_statement_evidence_id = defendant_statement["documents"][0]["id"]

        now += timedelta(seconds=15)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "02-02-update-defendant-statement.http",
                method="patch",
                url=f"/violation_reports/{violation_report_id}/defendantStatements/{defendant_statement_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={"data": {"description": "В усьому винні бобри. Обіцяли, що більше не будуть."}},
            )
            assert resp.status == 200, await resp.text()

        # delete document
        now += timedelta(seconds=15)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "02-03-delete-document.http",
                method="delete",
                url=f"/violation_reports/{violation_report_id}/defendantStatements/{defendant_statement_id}/documents/{defendant_statement_evidence_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
            )
            assert resp.status == 204, await resp.text()

        # post another evidence doc
        now += timedelta(seconds=15)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "02-04-post-defendant-document.http",
                method="post",
                url=f"/violation_reports/{violation_report_id}/defendantStatements/{defendant_statement_id}/documents",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "title": "defendant_statement_2.pdf",
                        "url": generate_test_doc_url(sub_app, doc_hash="b" * 32),
                        "hash": "md5:" + "b" * 32,
                        "format": "application/pdf",
                        "documentType": "violationReportEvidence",
                    }
                },
            )
            assert resp.status == 201, await resp.text()
            defendant_statement_evidence_id = (await resp.json())["data"]["id"]

        now += timedelta(seconds=15)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "02-05-put-defendant-statement-evidence.http",
                method="put",
                url=f"/violation_reports/{violation_report_id}/defendantStatements/{defendant_statement_id}/documents/{defendant_statement_evidence_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "title": "ai_generated_beavers_0001.gif",
                        "url": generate_test_doc_url(sub_app, doc_hash="2" * 32),
                        "hash": "md5:" + "2" * 32,
                        "format": "image/gif",
                        "documentType": "violationReportEvidence",
                    }
                },
            )
            assert resp.status == 201, await resp.text()

        # update document description
        now += timedelta(seconds=35)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "02-06-patch-defendant-statement-evidence.http",
                method="patch",
                url=f"/violation_reports/{violation_report_id}/defendantStatements/{defendant_statement_id}/documents/{defendant_statement_evidence_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "title": "доказ_оновлений.pdf",
                        "description": "Докази причетності бобрів.",
                        "description_en": "Evidence of beaver involvement.",
                    }
                },
            )
            assert resp.status == 200, await resp.text()

        now += timedelta(seconds=15)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "02-08-publish-defendant-statement.http",
                method="patch",
                url=f"/violation_reports/{violation_report_id}/defendantStatements/{defendant_statement_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={"data": {"status": "active"}},
            )
            assert resp.status == 200, await resp.text()

        # --<<== Decision =>>=-- #
        # post decision
        now = datetime.fromisoformat(defendant_period_end) + timedelta(hours=10, minutes=15)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "03-01-create-decision.http",
                method="post",
                url=f"/violation_reports/{violation_report_id}/decisions",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "resolution": "satisfied",
                        "description": "Суворо засуджуємо бобрів.",
                        "documents": [
                            {
                                "title": "protocol.pdf",
                                "url": generate_test_doc_url(sub_app),
                                "hash": "md5:" + "0" * 32,
                                "format": "application/pdf",
                                "documentType": "violationReportEvidence",
                            }
                        ],
                    }
                },
            )
            assert resp.status == 201, await resp.text()
            decision = (await resp.json())["data"]
            decision_id = decision["id"]
            protocol_id = decision["documents"][0]["id"]

        # add decision signature
        now += timedelta(seconds=12)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "03-02-post-decision-signature.http",
                method="post",
                url=f"/violation_reports/{violation_report_id}/decisions/{decision_id}/documents",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "title": "sign.p7s",
                        "url": generate_test_doc_url(sub_app),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pkcs7-signature",
                        "documentType": "violationReportSignature",
                    }
                },
            )
            assert resp.status == 201, await resp.text()
            result = await resp.json()
            signature_id = result["data"]["id"]

        # change decision
        now += timedelta(seconds=12)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "03-03-change-decision.http",
                method="patch",
                url=f"/violation_reports/{violation_report_id}/decisions/{decision_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "resolution": "declinedNoViolation",
                        "description": 'Комісія дійшла висновку, що ці бобри не підпадають під гриф "таємно" або "для службового користування".',
                    }
                },
            )
            assert resp.status == 200, await resp.text()

        # delete document
        now += timedelta(seconds=15)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "03-04-delete-document.http",
                method="delete",
                url=f"/violation_reports/{violation_report_id}/decisions/{decision_id}/documents/{protocol_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
            )
            assert resp.status == 204, await resp.text()

        # post another doc
        now += timedelta(seconds=15)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "03-05-post-decision-document.http",
                method="post",
                url=f"/violation_reports/{violation_report_id}/decisions/{decision_id}/documents",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "title": "protocol(2).pdf",
                        "url": generate_test_doc_url(sub_app, doc_hash="f" * 32),
                        "hash": "md5:" + "f" * 32,
                        "format": "application/pdf",
                        "documentType": "violationReportEvidence",
                    }
                },
            )
            assert resp.status == 201, await resp.text()

        # update signature
        now += timedelta(seconds=12)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "03-06-put-decision-signature.http",
                method="put",
                url=f"/violation_reports/{violation_report_id}/decisions/{decision_id}/documents/{signature_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "title": "sign_1.p7s",
                        "url": generate_test_doc_url(sub_app, doc_hash="3" * 32),
                        "hash": "md5:" + "3" * 32,
                        "format": "application/pkcs7-signature",
                        "documentType": "violationReportSignature",
                    }
                },
            )
            assert resp.status == 201, await resp.text()

        # publish decision
        now += timedelta(seconds=2)
        with freeze_time(now):
            resp = await request_to_http(
                filename=TARGET_DIR + "03-07-publish-decision.http",
                method="patch",
                url=f"/violation_reports/{violation_report_id}/decisions/{decision_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "status": "active",
                    }
                },
            )
            assert resp.status == 200, await resp.text()

        # get violation report
        resp = await request_to_http(
            filename=TARGET_DIR + "04-01-get-violation-report.http",
            method="get",
            url=f"/violation_reports/{violation_report_id}",
        )
        assert resp.status == 200, await resp.text()

        # get feed
        resp = await request_to_http(
            filename=TARGET_DIR + "05-01-feed.http",
            method="get",
            url="/violation_reports",
        )
        assert resp.status == 200, await resp.text()
        result = await resp.json()
        offset = result["next_page"]["offset"]

        resp = await request_to_http(
            filename=TARGET_DIR + "05-02-feed-empty.http",
            method="get",
            url=f"/violation_reports?offset={offset}",
        )
        assert resp.status == 200, await resp.text()

    async def test_errors(self, deterministic_environment, request_to_http, sub_app, api):
        now = datetime.fromisoformat("2025-10-12T15:35:35+03:00")
        target_dir = f"{TARGET_DIR}/errors/"
        with freeze_time(now):
            contract = await ContractFactory.create()
            tender = await TenderFactory.create(_id=contract.tender_id)
            await AgreementFactory.create(_id=tender.agreement.id)

        with freeze_time(now):
            # fail post pending pending report
            resp = await request_to_http(
                filename=target_dir + "00-01-post-pending-fail.http",
                method="post",
                url=f"/contracts/{contract.id}/violation_reports",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "details": {
                            "reason": ViolationReportReason.contractBreach,
                            "description": "Постачальник порушив контракт.",
                        },
                        "status": ViolationReportStatus.pending,
                    }
                },
            )
            assert resp.status == 400, await resp.text()
            result = await resp.json()
            assert result == {
                "type": "data-validation",
                "title": "Data Validation Error",
                "details": "Validation errors in body",
                "status": 400,
                "errors": [
                    {
                        "type": "status_error",
                        "loc": ["data", "status"],
                        "msg": "pending should be draft.",
                        "input": "pending",
                        "ctx": {"status": "pending"},
                    }
                ],
            }

        with freeze_time(now):
            resp = await api.post(
                path=f"/contracts/{contract.id}/violation_reports",
                headers={"Authorization": f"Bearer {BROKER}"},
                json={
                    "data": {
                        "details": {
                            "reason": ViolationReportReason.contractBreach,
                            "description": "Постачальник порушив контракт.",
                        }
                    }
                },
            )

        assert resp.status == 201, await resp.text()
        result = await resp.json()
        assert result["data"]["status"] == "draft"
        assert "defendantPeriod" not in result["data"]
        violation_report = result["data"]
        violation_report_id = violation_report["id"]

        resp = await request_to_http(
            filename=target_dir + "01-00-get-report.http",
            method="get",
            url=f"/violation_reports/{violation_report_id}",
            headers={"Authorization": f"Bearer {BROKER}"},
        )
        assert resp.status == 200, await resp.text()

        # fail add defendantStatement
        resp = await request_to_http(
            filename=target_dir + "01-01-put-defendant-statement.http",
            method="post",
            url=f"/violation_reports/{violation_report_id}/defendantStatements",
            headers={"Authorization": f"Bearer {BROKER}"},
            json_data={"data": {"description": "В усьому винні бобри. Обіцяли, що більше не будуть."}},
        )
        assert resp.status == 400, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-bad-request",
            "title": "Bad Request",
            "details": "Can add defendantStatement only during defendantPeriod.",
            "status": 400,
            "now": ANY,
            "period": None,
        }

        #  fail add defendantStatement document
        resp = await request_to_http(
            filename=target_dir + "01-02-defendant-statement-document.http",
            method="post",
            url=f"/violation_reports/{violation_report_id}/defendantStatements/{'a' * 32}/documents",
            headers={"Authorization": f"Bearer {BROKER}"},
            json_data={
                "data": {
                    "title": "ai_generated_beavers_0001.gif",
                    "url": generate_test_doc_url(sub_app, doc_hash="2" * 32),
                    "hash": "md5:" + "2" * 32,
                    "format": "image/gif",
                    "documentType": "violationReportEvidence",
                }
            },
        )
        assert resp.status == 404, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-not-found",
            "title": "Not Found",
            "details": "defendantStatement not found.",
            "status": 404,
        }

        # fail add decision
        resp = await request_to_http(
            filename=target_dir + "01-03-put-decision.http",
            method="post",
            url=f"/violation_reports/{violation_report_id}/decisions",
            headers={"Authorization": f"Bearer {BROKER}"},
            json_data={
                "data": {
                    "resolution": "declinedNoViolation",
                    "description": 'Комісія дійшла висновку, що ці карти не підпадають під гриф "таємно" або "для службового користування".',
                }
            },
        )
        assert resp.status == 400, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-bad-request",
            "title": "Bad Request",
            "details": "Can change decision only after defendantPeriod.endDate.",
            "status": 400,
            "now": ANY,
            "period": None,
        }

        # fail add decision document
        resp = await request_to_http(
            filename=target_dir + "01-04-post-decision-document.http",
            method="post",
            url=f"/violation_reports/{violation_report_id}/decisions/{'1' * 32}/documents",
            headers={"Authorization": f"Bearer {BROKER}"},
            json_data={
                "data": {
                    "title": "sign.p7s",
                    "url": generate_test_doc_url(sub_app),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pkcs7-signature",
                    "documentType": "violationReportSignature",
                }
            },
        )
        assert resp.status == 404, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-not-found",
            "title": "Not Found",
            "details": "decision not found.",
            "status": 404,
        }

        # fail patch violation report with extra fields
        resp = await request_to_http(
            filename=target_dir + "01-05-patch-report-extra.http",
            method="patch",
            url=f"/violation_reports/{violation_report_id}",
            headers={"Authorization": f"Bearer {BROKER}"},
            json_data={
                "data": {
                    "tender_id": "1" * 32,
                    "status": "pending",
                    "reason": ViolationReportReason.goodsNonCompliance,
                }
            },
        )
        assert resp.status == 400, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "data-validation",
            "title": "Data Validation Error",
            "details": "Validation errors in body",
            "status": 400,
            "errors": [
                {
                    "type": "missing",
                    "loc": ["data", "ViolationReportPatchDetailsRequestData", "details"],
                    "msg": "Field required",
                    "input": {
                        "tender_id": "11111111111111111111111111111111",
                        "status": "pending",
                        "reason": "goodsNonCompliance",
                    },
                },
                {
                    "type": "extra_forbidden",
                    "loc": ["data", "ViolationReportPatchDetailsRequestData", "tender_id"],
                    "msg": "Extra inputs are not permitted",
                    "input": "11111111111111111111111111111111",
                },
                {
                    "type": "extra_forbidden",
                    "loc": ["data", "ViolationReportPatchDetailsRequestData", "status"],
                    "msg": "Extra inputs are not permitted",
                    "input": "pending",
                },
                {
                    "type": "extra_forbidden",
                    "loc": ["data", "ViolationReportPatchDetailsRequestData", "reason"],
                    "msg": "Extra inputs are not permitted",
                    "input": "goodsNonCompliance",
                },
                {
                    "type": "extra_forbidden",
                    "loc": ["data", "ViolationReportPublishRequestData", "tender_id"],
                    "msg": "Extra inputs are not permitted",
                    "input": "11111111111111111111111111111111",
                },
                {
                    "type": "extra_forbidden",
                    "loc": ["data", "ViolationReportPublishRequestData", "reason"],
                    "msg": "Extra inputs are not permitted",
                    "input": "goodsNonCompliance",
                },
            ],
        }

        now += timedelta(seconds=36)
        with freeze_time(now):
            resp = await request_to_http(
                filename=target_dir + "01-06-patch-report-no-changes.http",
                method="patch",
                url=f"/violation_reports/{violation_report_id}",
                headers={"Authorization": f"Bearer {BROKER}"},
                json_data={
                    "data": {
                        "details": {
                            "reason": violation_report["details"]["reason"],
                            "description": violation_report["details"]["description"],
                        },
                    }
                },
            )
            assert resp.status == 200, await resp.text()
            result = (await resp.json())["data"]
            assert result["details"]["dateModified"] == violation_report["details"]["dateModified"]
            assert result["dateModified"] == violation_report["dateModified"]
