from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

from prozorro_cdb.api.database.schema.document import DocumentTypes
from prozorro_cdb.violation_report.database.schema.violation_report import (
    ViolationReportStatus,
)

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
        assert resp.status == HTTPStatus.NOT_FOUND, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-not-found",
            "title": "Not Found",
            "details": "Violation Report not found.",
            "status": HTTPStatus.NOT_FOUND,
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
        assert resp.status == HTTPStatus.NOT_FOUND, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-not-found",
            "title": "Not Found",
            "details": "Document not found.",
            "status": HTTPStatus.NOT_FOUND,
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
        assert resp.status == HTTPStatus.OK, await resp.text()
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
        assert resp.status == HTTPStatus.OK, await resp.text()
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
        assert resp.status == HTTPStatus.OK, await resp.text()
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
        assert resp.status == HTTPStatus.CREATED, await resp.text()
        result = await resp.json()

        # updates
        assert result["data"]["title"] == "evidences.doc"
        assert result["data"]["dateModified"] > initial_document["dateModified"]
        assert result["data"]["datePublished"] > initial_document["datePublished"]

        # cannot change
        assert result["data"]["id"] == document.id
        assert result["data"]["documentType"] == DocumentTypes.violationReportSignature

    async def test_put_details_previous_versions(self, api, sub_app):
        document = DocumentFactory.build(documentType=DocumentTypes.violationReportEvidence, title="evidences_v1.doc")
        violation_report = await ViolationReportDBModelFactory.create(
            details=ReportDetailsFactory.build(documents=[document])
        )

        resp = await api.put(
            f"/violation_reports/{violation_report.id}/details/documents/{document.id}",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "title": "evidences_v2.doc",
                    "url": generate_test_doc_url(sub_app),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "documentType": "violationReportEvidence",
                }
            },
        )
        assert resp.status == HTTPStatus.CREATED, await resp.text()

        resp = await api.get(f"/violation_reports/{violation_report.id}/details/documents/{document.id}")
        assert resp.status == HTTPStatus.OK, await resp.text()
        result = await resp.json()

        assert result["data"]["title"] == "evidences_v2.doc"
        assert len(result["data"]["previousVersions"]) == 1
        assert result["data"]["previousVersions"][0]["title"] == document.title
        assert result["data"]["previousVersions"][0]["dateModified"] == document.dateModified.isoformat()


class TestPostDetailsDocument:
    async def test_post_duplicate_signature(self, api, signature_payload):
        signature = DocumentFactory.build(documentType=DocumentTypes.violationReportSignature)
        violation_report = await ViolationReportDBModelFactory.create(
            details=ReportDetailsFactory.build(documents=[signature])
        )

        resp = await api.post(
            f"/violation_reports/{violation_report.id}/details/documents",
            auth=BROKER_AUTH,
            json={"data": signature_payload()},
        )
        assert resp.status == HTTPStatus.BAD_REQUEST, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-bad-request",
            "title": "Bad Request",
            "details": "Signature document already exists. Update it with PUT method instead.",
            "status": HTTPStatus.BAD_REQUEST,
        }


class TestDetailsDocumentStatusLocked:
    async def test_post_forbidden_after_publish(self, api, sub_app):
        violation_report = await ViolationReportDBModelFactory.create(status=ViolationReportStatus.pending)

        resp = await api.post(
            f"/violation_reports/{violation_report.id}/details/documents",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "title": "evidence.doc",
                    "url": generate_test_doc_url(sub_app),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "documentType": "violationReportEvidence",
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

    async def test_patch_forbidden_after_publish(self, api):
        document = DocumentFactory.build(documentType=DocumentTypes.violationReportEvidence)
        violation_report = await ViolationReportDBModelFactory.create(
            status=ViolationReportStatus.pending,
            details=ReportDetailsFactory.build(documents=[document]),
        )

        resp = await api.patch(
            f"/violation_reports/{violation_report.id}/details/documents/{document.id}",
            auth=BROKER_AUTH,
            json={"data": {"title": "новий підпис"}},
        )
        assert resp.status == HTTPStatus.BAD_REQUEST, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-bad-request",
            "title": "Bad Request",
            "details": "Details update forbidden in 'pending' status",
            "status": HTTPStatus.BAD_REQUEST,
        }

    async def test_put_forbidden_after_publish(self, api, sub_app):
        document = DocumentFactory.build(documentType=DocumentTypes.violationReportEvidence)
        violation_report = await ViolationReportDBModelFactory.create(
            status=ViolationReportStatus.pending,
            details=ReportDetailsFactory.build(documents=[document]),
        )

        resp = await api.put(
            f"/violation_reports/{violation_report.id}/details/documents/{document.id}",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "title": "evidence_v2.doc",
                    "url": generate_test_doc_url(sub_app),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "documentType": "violationReportEvidence",
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

    async def test_delete_forbidden_after_publish(self, api):
        document = DocumentFactory.build(documentType=DocumentTypes.violationReportEvidence)
        violation_report = await ViolationReportDBModelFactory.create(
            status=ViolationReportStatus.pending,
            details=ReportDetailsFactory.build(documents=[document]),
        )

        resp = await api.delete(
            f"/violation_reports/{violation_report.id}/details/documents/{document.id}",
            auth=BROKER_AUTH,
        )
        assert resp.status == HTTPStatus.BAD_REQUEST, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-bad-request",
            "title": "Bad Request",
            "details": "Details update forbidden in 'pending' status",
            "status": HTTPStatus.BAD_REQUEST,
        }


class TestDownloadDetailsDocument:
    async def test_download_redirect(self, api, sub_app):
        violation_report = await ViolationReportDBModelFactory.create(details=ReportDetailsFactory.build(documents=[]))

        resp = await api.post(
            f"/violation_reports/{violation_report.id}/details/documents",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "title": "evidence.doc",
                    "url": generate_test_doc_url(sub_app),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "documentType": "violationReportEvidence",
                }
            },
        )
        assert resp.status == HTTPStatus.CREATED, await resp.text()
        result = await resp.json()
        document_id = result["data"]["id"]
        download_key = parse_qs(urlparse(result["data"]["url"]).query)["download"][0]

        resp = await api.get(
            f"/violation_reports/{violation_report.id}/details/documents/{document_id}?download={download_key}",
            allow_redirects=False,
        )
        assert resp.status == HTTPStatus.FOUND, await resp.text()
        assert "Signature=" in resp.headers["Location"]
        assert "KeyID=" in resp.headers["Location"]

    async def test_download_wrong_key_not_found(self, api, sub_app):
        violation_report = await ViolationReportDBModelFactory.create(details=ReportDetailsFactory.build(documents=[]))

        resp = await api.post(
            f"/violation_reports/{violation_report.id}/details/documents",
            auth=BROKER_AUTH,
            json={
                "data": {
                    "title": "evidence.doc",
                    "url": generate_test_doc_url(sub_app),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "documentType": "violationReportEvidence",
                }
            },
        )
        assert resp.status == HTTPStatus.CREATED, await resp.text()
        document_id = (await resp.json())["data"]["id"]

        resp = await api.get(
            f"/violation_reports/{violation_report.id}/details/documents/{document_id}?download=wrong_key",
        )
        assert resp.status == HTTPStatus.NOT_FOUND, await resp.text()
        result = await resp.json()
        assert result == {
            "type": "http-not-found",
            "title": "Not Found",
            "details": "Document not found.",
            "status": HTTPStatus.NOT_FOUND,
        }
