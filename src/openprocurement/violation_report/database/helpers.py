import logging
from typing import Optional

from aiohttp import web
from pymongo.errors import DuplicateKeyError

from openprocurement.api.context_async import get_now_async
from openprocurement.api.database_async import get_mongodb
from openprocurement.violation_report.database.schema.contract import Contract
from openprocurement.violation_report.database.schema.violation_report import (
    ViolationReportDBModel,
)

logger = logging.getLogger(__name__)


class CreateViolationReportDuplicateError(Exception):
    def __init__(self, *args, duplicate_of) -> None:
        self.duplicate_of = duplicate_of
        super().__init__(*args)


async def get_contract_or_404(contract_id: str) -> Contract:
    db = get_mongodb()
    contract = await db.contract.get(contract_id)
    if contract is None:
        raise web.HTTPNotFound(text="Contract not found.")
    return Contract.model_validate(contract)


async def create_violation_report(violation_report: ViolationReportDBModel) -> ViolationReportDBModel:
    db = get_mongodb()
    try:
        report = await db.violation_reports.save(violation_report, insert=True)
    except DuplicateKeyError:
        unique_keys = {
            "tender_id": violation_report.tender_id,
            "buyer.identifier.id": violation_report.buyer.identifier.id,
            "suppliers.identifier.id": {"$in": [s.identifier.id for s in violation_report.suppliers]},
        }
        duplicates = await db.violation_reports.find(unique_keys)
        if not duplicates:
            raise RuntimeError(f"Unexpected duplicate with: {unique_keys}")

        duplicate_of = duplicates[0]["_id"]
        logger.info(
            "Violation report duplicate",
            extra={
                "unique_keys": unique_keys,
                "duplicate_of": duplicate_of,
            },
        )
        raise CreateViolationReportDuplicateError(duplicate_of=duplicate_of)

    return report


async def update_violation_report(violation_report: ViolationReportDBModel) -> ViolationReportDBModel:
    db = get_mongodb()
    return await db.violation_reports.save(violation_report, insert=False)


async def get_violation_report_or_404(violation_report_id: str) -> ViolationReportDBModel:
    db = get_mongodb()
    obj = await db.violation_reports.get(violation_report_id)
    if obj is None:
        raise web.HTTPNotFound(text="Violation Report not found.")
    return ViolationReportDBModel.model_validate(obj)


async def get_tender_violation_reports(
    tender_id: str, contract_id: Optional[str] = None
) -> list[ViolationReportDBModel]:
    db = get_mongodb()
    filters = {"tender_id": tender_id}
    if contract_id is not None:
        filters["contract_id"] = contract_id
    objs = await db.violation_reports.find(filters)
    return [ViolationReportDBModel.model_validate(obj) for obj in objs]


async def get_violation_report_id() -> str:
    db = get_mongodb()
    ctime = get_now_async().date()
    index = await db.sequences.get_next_value(f"violation_report_{ctime.isoformat()}")
    return "UA-{:04}-{:02}-{:02}-{:06}".format(
        ctime.year,
        ctime.month,
        ctime.day,
        index,
    )
