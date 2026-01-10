import logging
from typing import Optional

from aiohttp import web

from openprocurement.tender.pricequotation.constants import PQ
from prozorro_cdb.api.context import get_now_async
from prozorro_cdb.api.database.store import get_mongodb
from prozorro_cdb.violation_report.database.schema.agreement import Agreement
from prozorro_cdb.violation_report.database.schema.contract import Contract
from prozorro_cdb.violation_report.database.schema.tender import Tender
from prozorro_cdb.violation_report.database.schema.violation_report import (
    ViolationReportDBModel,
)

logger = logging.getLogger(__name__)


async def get_contract_or_404(contract_id: str) -> Contract:
    db = get_mongodb()
    contract = await db.contract.get(contract_id)
    if contract is None:
        raise web.HTTPNotFound(text="Contract not found.")
    return Contract.model_validate(contract)


async def get_pq_tender_or_error(tender_id: str) -> Tender:
    db = get_mongodb()
    tender = await db.tender.get(tender_id)
    if tender is None:
        raise web.HTTPNotFound(text="Tender not found.")
    if tender["procurementMethodType"] != PQ:
        raise web.HTTPBadRequest(text="priceQuotation procedure expected.")
    return Tender.model_validate(tender)


async def get_agreement_or_404(agreement_id: str) -> Agreement:
    db = get_mongodb()
    tender = await db.agreement.get(agreement_id)
    if tender is None:
        raise web.HTTPNotFound(text="Agreement not found.")
    return Agreement.model_validate(tender)


async def create_violation_report(violation_report: ViolationReportDBModel) -> ViolationReportDBModel:
    db = get_mongodb()
    return await db.violation_report.save(violation_report, insert=True)


async def update_violation_report(
    violation_report: ViolationReportDBModel,
    modified: bool = True,
) -> ViolationReportDBModel:
    db = get_mongodb()
    return await db.violation_report.save(violation_report, insert=False, modified=modified)


async def get_violation_report_or_404(violation_report_id: str) -> ViolationReportDBModel:
    db = get_mongodb()
    obj = await db.violation_report.get(violation_report_id)
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
    objs = await db.violation_report.find(filters)
    return [ViolationReportDBModel.model_validate(obj) for obj in objs]


async def get_violation_report_pretty_id() -> str:
    db = get_mongodb()
    ctime = get_now_async().date()
    index = await db.sequences.get_next_value(f"violation_report_{ctime.isoformat()}")
    return "UA-D-{:04}-{:02}-{:02}-{:06}".format(
        ctime.year,
        ctime.month,
        ctime.day,
        index,
    )
