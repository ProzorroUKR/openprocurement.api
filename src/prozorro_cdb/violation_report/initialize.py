from prozorro_cdb.api.application import Application

from .database.collection import ViolationReportCollection
from .handlers import (
    decision,
    defendant_statement,
    violation_report,
    violation_report_details,
)


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
        violation_report.ViolationReportView,
        name=violation_report.ViolationReportView.view_name,
    )
    app.router.add_view(
        "/violation_reports/{violation_report_id}/details",
        violation_report_details.ViolationReportDetailsView,
        name=violation_report_details.ViolationReportDetailsView.view_name,
    )
    app.router.add_view(
        "/violation_reports/{violation_report_id}/details/documents",
        violation_report_details.ViolationReportDocumentListView,
        name=violation_report_details.ViolationReportDocumentListView.view_name,
    )
    app.router.add_view(
        "/violation_reports/{violation_report_id}/details/documents/{document_id}",
        violation_report_details.ViolationReportDocumentView,
        name=violation_report_details.ViolationReportDocumentView.view_name,
    )

    app.router.add_view(
        "/violation_reports/{violation_report_id}/defendantStatements",
        defendant_statement.DefendantStatementListView,
        name=defendant_statement.DefendantStatementListView.view_name,
    )
    app.router.add_view(
        "/violation_reports/{violation_report_id}/defendantStatements/{defendant_statement_id}",
        defendant_statement.DefendantStatementView,
        name=defendant_statement.DefendantStatementView.view_name,
    )
    app.router.add_view(
        "/violation_reports/{violation_report_id}/defendantStatements/{defendant_statement_id}/documents",
        defendant_statement.DefendantStatementDocumentListView,
        name=defendant_statement.DefendantStatementDocumentListView.view_name,
    )
    app.router.add_view(
        "/violation_reports/{violation_report_id}/defendantStatements/{defendant_statement_id}/documents/{document_id}",
        defendant_statement.DefendantStatementDocumentView,
        name=defendant_statement.DefendantStatementDocumentView.view_name,
    )

    app.router.add_view(
        "/violation_reports/{violation_report_id}/decisions",
        decision.ViolationReportDecisionListView,
        name=decision.ViolationReportDecisionListView.view_name,
    )
    app.router.add_view(
        "/violation_reports/{violation_report_id}/decisions/{decision_id}",
        decision.ViolationReportDecisionView,
        name=decision.ViolationReportDecisionView.view_name,
    )
    app.router.add_view(
        "/violation_reports/{violation_report_id}/decisions/{decision_id}/documents",
        decision.ViolationReportDecisionDocumentListView,
        name=decision.ViolationReportDecisionDocumentListView.view_name,
    )
    app.router.add_view(
        "/violation_reports/{violation_report_id}/decisions/{decision_id}/documents/{document_id}",
        decision.ViolationReportDecisionDocumentView,
        name=decision.ViolationReportDecisionDocumentView.view_name,
    )

    # -- database --
    app.db.add_collection(
        ViolationReportCollection.object_name,
        ViolationReportCollection,
    )
