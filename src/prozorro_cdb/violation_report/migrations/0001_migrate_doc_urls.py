import asyncio
import os
from re import compile
from typing import Callable

import sentry_sdk

from prozorro_cdb.api.migrations.utils import BaseMigrationArgumentParser, CollectionMigration
from prozorro_cdb.violation_report.database.collection import ViolationReportCollection

URL_PATTERN = compile(r"(?P<base_url>.*)/documents/(\w+)\?download=(?P<download_key>.*)")


def fix_docs(docs: list[dict], fix_base_url: Callable = None):
    for d in docs:
        if search_res := URL_PATTERN.search(d.get("url", "")):
            base_url = search_res.group("base_url")
            if fix_base_url is not None:
                base_url = fix_base_url(base_url)
            d["url"] = f"{base_url}/documents/{d['id']}?download={search_res.group('download_key')}"


class Migration(CollectionMigration):
    collection_cls = ViolationReportCollection

    append_revision = False
    update_date_modified = False
    update_feed_position = True

    def update_obj(self, doc: dict):
        if details := doc.get("details", {}):
            fix_docs(details.get("documents", []), lambda x: x if x.endswith("/details") else x + "/details")
        for def_statement in doc.get("defendantStatements", []):
            fix_docs(def_statement.get("documents", []))
        for decision in doc.get("decisions", []):
            fix_docs(decision.get("documents", []))

        return doc

    def get_projection(self) -> dict:
        return {"details": 1, "defendantStatements": 1, "decisions": 1}


if __name__ == "__main__":
    # python src/prozorro_cdb/violation_report/migrations/0001_migrate_doc_urls.py -p <path to service.ini>

    os.environ["NO_GEVENT_MONKEY_PATCH"] = "1"
    from openprocurement.api.app import load_config

    args = BaseMigrationArgumentParser().parse_args()
    settings = load_config(args.p)["app:main"]

    if dsn := settings.get("sentry.dsn"):
        sentry_sdk.init(dsn=dsn)

    migration = Migration(settings, args.b)
    asyncio.run(migration.run())
