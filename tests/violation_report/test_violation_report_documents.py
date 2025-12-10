from prozorro_cdb.api.database.schema.document import DocumentTypes

from ..base import BROKER_AUTH
from ..conftest import generate_test_doc_url
from ..factories.violation_report import (
    DocumentFactory,
    ReportDetailsFactory,
    ViolationReportDBModelFactory,
)


class TestPatchDetailsDocument:
    async def test_patch_not_found_report(self, api):
        resp = await api.patch(
            f"/violation_reports/{'a' * 32}/details/documents/{'a' * 32}",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "title": "Підпис",
                }
            },
        )
        assert resp.status == 404, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-not-found",
            "title": "Not Found",
            "details": "Violation Report not found.",
            "status": 404,
        }

    async def test_patch_not_found_document(self, api):
        violation_report = await ViolationReportDBModelFactory.create()

        resp = await api.patch(
            f"/violation_reports/{violation_report.id}/details/documents/{'a' * 32}",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "title": "Підпис",
                }
            },
        )
        assert resp.status == 404, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-not-found",
            "title": "Not Found",
            "details": "Document not found.",
            "status": 404,
        }

    async def test_patch_details(self, api):
        document = DocumentFactory.build(documentType=DocumentTypes.violationReportEvidence)
        violation_report = await ViolationReportDBModelFactory.create(
            details=ReportDetailsFactory.build(documents=[document])
        )

        resp = await api.patch(
            f"/violation_reports/{violation_report.id}/details/documents/{document.id}",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "title": "Підпис",
                }
            },
        )
        assert resp.status == 200, await resp.text()
        result = await resp.json()

        assert result["data"]["title"] == "Підпис"
        assert result["data"]["dateModified"] > document.dateModified.isoformat()

    async def test_patch_empty(self, api):
        document = DocumentFactory.build(
            title="Підпис",
        )
        violation_report = await ViolationReportDBModelFactory.create(
            details=ReportDetailsFactory.build(documents=[document])
        )

        resp = await api.patch(
            f"/violation_reports/{violation_report.id}/details/documents/{document.id}",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "title": "Підпис",
                }
            },
        )
        assert resp.status == 200, await resp.text()
        result = await resp.json()

        assert result["data"]["title"] == "Підпис"
        assert result["data"]["dateModified"] == document.dateModified.isoformat()  # the same as before


class TestPutDetailsDocument:
    async def test_put_details(self, api, sub_app):
        document = DocumentFactory.build(documentType=DocumentTypes.violationReportSignature, format="sign/p7s")
        violation_report = await ViolationReportDBModelFactory.create(
            details=ReportDetailsFactory.build(documents=[document])
        )

        resp = await api.get(f"/violation_reports/{violation_report.id}/details/documents/{document.id}")
        assert resp.status == 200, await resp.text()
        result = await resp.json()
        initial_document = result["data"]

        resp = await api.put(
            f"/violation_reports/{violation_report.id}/details/documents/{document.id}",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "title": "evidences.doc",
                    "url": generate_test_doc_url(sub_app),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "documentType": "violationReportEvidence",
                }
            },
        )
        assert resp.status == 201, await resp.text()
        result = await resp.json()

        # updates
        assert result["data"]["title"] == "evidences.doc"
        assert result["data"]["dateModified"] > initial_document["dateModified"]
        assert result["data"]["datePublished"] > initial_document["datePublished"]

        # cannot change
        assert result["data"]["id"] == document.id
        assert result["data"]["documentType"] == DocumentTypes.violationReportSignature
