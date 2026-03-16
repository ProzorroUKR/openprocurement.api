from importlib import import_module

import pytest

from prozorro_cdb.api.database.schema.document import DocumentTypes
from tests.factories.violation_report import (
    DecisionFactory,
    DefendantStatementFactory,
    DocumentFactory,
    ReportDetailsFactory,
    ViolationReportDBModelFactory,
)

migration_module = import_module("prozorro_cdb.violation_report.migrations.0001_migrate_doc_urls")


@pytest.mark.parametrize(
    ("data", "check_results"),
    [
        pytest.param(
            {
                "details": ReportDetailsFactory.build(
                    documents=[
                        DocumentFactory.build(
                            id="a" * 32,
                            documentType=DocumentTypes.violationReportEvidence,
                            url="/violation_reports/dfe1ddd181e74db3ae5a902e19e9b3c5/documents/"
                            "0a58ea0077954c6697e1e3c1f072e08f?download=070bb2eff5584e3f87e9d8495e887f06",
                        )
                    ]
                ),
                "decisions": [
                    DecisionFactory.build(
                        documents=[
                            DocumentFactory.build(
                                id="b" * 32,
                                documentType=DocumentTypes.violationReportEvidence,
                                url="/violation_reports/dfe1ddd181e74db3ae5a902e19e9b3c5/decisions/"
                                "98ef60faa69d4e179e6861778a8e559f/documents/"
                                "59af10d5ab6b44259d83e22d945a6c92?download=7b7c46dd8bb54f88b6e925cb1b6d26b8",
                            )
                        ]
                    )
                ],
                "defendantStatements": [
                    DefendantStatementFactory.build(
                        documents=[
                            DocumentFactory.build(
                                id="c" * 32,
                                documentType=DocumentTypes.violationReportEvidence,
                                url="/violation_reports/dfe1ddd181e74db3ae5a902e19e9b3c5/defendantStatements/"
                                "c20261437c5e4c19b197309fa3ba4443/documents/"
                                "bb4ed17300eb4cf0991ef5f68571e8fd?download=070bb2eff5584e3f87e9d8495e887f06",
                            )
                        ]
                    )
                ],
            },
            lambda updated_data, violation_report: (
                "public_modified" in updated_data,
                updated_data["public_modified"] != violation_report.public_modified,
                updated_data["dateModified"] == violation_report.dateModified.isoformat(),
                updated_data["_rev"] != violation_report.rev,
                # check if details has more data except documents
                set(updated_data["details"].keys()) - {"documents"},
                updated_data["details"]["documents"][0]["url"] != violation_report.details.documents[0].url,
                updated_data["details"]["documents"][0]["url"]
                == f"/violation_reports/dfe1ddd181e74db3ae5a902e19e9b3c5/documents/{"a" * 32}?download=070bb2eff5584e3f87e9d8495e887f06",
                # check if decisions has more data except documents
                set(updated_data["decisions"][0].keys()) - {"documents"},
                updated_data["decisions"][0]["documents"][0]["url"] != violation_report.decisions[0].documents[0].url,
                updated_data["decisions"][0]["documents"][0]["url"]
                == f"/violation_reports/dfe1ddd181e74db3ae5a902e19e9b3c5/decisions/98ef60faa69d4e179e6861778a8e559f/documents/{"b" * 32}?download=7b7c46dd8bb54f88b6e925cb1b6d26b8",
                # check if defendantStatements has more data except documents
                set(updated_data["defendantStatements"][0].keys()) - {"documents"},
                updated_data["defendantStatements"][0]["documents"][0]["url"]
                != violation_report.defendantStatements[0].documents[0].url,
                updated_data["defendantStatements"][0]["documents"][0]["url"]
                == f"/violation_reports/dfe1ddd181e74db3ae5a902e19e9b3c5/defendantStatements/c20261437c5e4c19b197309fa3ba4443/documents/{"c" * 32}?download=070bb2eff5584e3f87e9d8495e887f06",
            ),
        ),
        pytest.param(
            {
                "details": ReportDetailsFactory.build(
                    documents=[
                        DocumentFactory.build(
                            id="a" * 32,
                            documentType=DocumentTypes.violationReportEvidence,
                            url=f"/violation_reports/dfe1ddd181e74db3ae5a902e19e9b3c5/documents/"
                            f"{"a" * 32}?download=070bb2eff5584e3f87e9d8495e887f06",
                        )
                    ]
                ),
                "decisions": [
                    DecisionFactory.build(
                        documents=[
                            DocumentFactory.build(
                                id="b" * 32,
                                documentType=DocumentTypes.violationReportEvidence,
                                url=f"/violation_reports/dfe1ddd181e74db3ae5a902e19e9b3c5/decisions/"
                                f"98ef60faa69d4e179e6861778a8e559f/documents/"
                                f"{"b" * 32}?download=7b7c46dd8bb54f88b6e925cb1b6d26b8",
                            )
                        ]
                    )
                ],
                "defendantStatements": [
                    DefendantStatementFactory.build(
                        documents=[
                            DocumentFactory.build(
                                id="c" * 32,
                                documentType=DocumentTypes.violationReportEvidence,
                                url=f"/violation_reports/dfe1ddd181e74db3ae5a902e19e9b3c5/defendantStatements/"
                                f"c20261437c5e4c19b197309fa3ba4443/documents/"
                                f"{"c" * 32}?download=070bb2eff5584e3f87e9d8495e887f06",
                            )
                        ]
                    )
                ],
            },
            lambda updated_data, violation_report: (
                "public_modified" in updated_data,
                updated_data["public_modified"] == violation_report.public_modified,
                updated_data["dateModified"] == violation_report.dateModified.isoformat(),
                updated_data["_rev"] == violation_report.rev,
                # check if details has more data except documents
                set(updated_data["details"].keys()) - {"documents"},
                updated_data["details"]["documents"][0]["url"] == violation_report.details.documents[0].url,
                # check if decisions has more data except documents
                set(updated_data["decisions"][0].keys()) - {"documents"},
                updated_data["decisions"][0]["documents"][0]["url"] == violation_report.decisions[0].documents[0].url,
                # check if defendantStatements has more data except documents
                set(updated_data["defendantStatements"][0].keys()) - {"documents"},
                updated_data["defendantStatements"][0]["documents"][0]["url"]
                == violation_report.defendantStatements[0].documents[0].url,
            ),
        ),
    ],
)
async def test_migration(api, data, check_results):
    violation_report = await ViolationReportDBModelFactory.create(**data)

    migration = migration_module.Migration()
    await migration.run()

    updated_data = await migration.collection.find_one({"_id": violation_report.id})
    assert all(check_results(updated_data, violation_report))
