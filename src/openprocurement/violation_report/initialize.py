from openprocurement.api.application import Application

from .database.collection import ViolationReportCollection
from .handlers import decision, defendant_statement, violation_report


def main(app: Application, *_) -> None:
    # -- routes --
    app.router.add_view(
        "/contracts/{contract_id}/violation_reports",
        violation_report.ContractViolationReportListView,
        name=violation_report.ContractViolationReportListView.view_name,
    )
    app.router.add_view(
        "/tender/{tender_id}/violation_reports",
        violation_report.TenderViolationReportListView,
    )
    app.router.add_view(
        "/violation_reports",
        violation_report.ViolationReportListView,
        name=violation_report.ViolationReportListView.view_name,
    )
    app.router.add_view(
        "/violation_reports/{violation_report_id}",
        violation_report.ViolationReportDetailsView,
        name=violation_report.ViolationReportDetailsView.view_name,
    )
    app.router.add_view(
        "/violation_reports/{violation_report_id}/documents/{document_id}",
        violation_report.ViolationReportDocumentView,
        name=violation_report.ViolationReportDocumentView.view_name,
    )

    app.router.add_view(
        "/violation_reports/{violation_report_id}/defendantStatement",
        defendant_statement.DefendantStatementView,
        name=defendant_statement.DefendantStatementView.view_name,
    )
    app.router.add_view(
        "/violation_reports/{violation_report_id}/defendantStatement/documents/{document_id}",
        defendant_statement.DefendantStatementDocumentView,
        name=defendant_statement.DefendantStatementDocumentView.view_name,
    )

    app.router.add_view(
        "/violation_reports/{violation_report_id}/decision",
        decision.ViolationReportDecisionView,
        name=decision.ViolationReportDecisionView.view_name,
    )
    app.router.add_view(
        "/violation_reports/{violation_report_id}/decision/documents/{document_id}",
        decision.ViolationReportDecisionDocumentView,
        name=decision.ViolationReportDecisionDocumentView.view_name,
    )

    # -- database --
    app.db.add_collection(
        ViolationReportCollection.object_name,
        ViolationReportCollection,
    )
