from datetime import datetime
from enum import StrEnum
from typing import Literal, Optional
from uuid import uuid4

from pydantic import Field, computed_field

from openprocurement.api.models_async.common import BaseModel, Period
from openprocurement.api.models_async.document import Document
from openprocurement.api.models_async.organization import (
    Buyer,
    ProcuringEntity,
    Supplier,
)


class ViolationReportReason(StrEnum):
    goodsNonCompliance = "goodsNonCompliance"
    contractBreach = "contractBreach"
    signingRefusal = "signingRefusal"


class ViolationReportDecisionStatus(StrEnum):
    satisfied = "satisfied"
    declinedNoViolation = "declinedNoViolation"
    declinedLackEvidence = "declinedLackEvidence"


class ViolationReportDecisionDBModel(BaseModel):
    status: ViolationReportDecisionStatus
    description: str = Field(description="Опис рішення", max_length=5_000)
    documents: list[Document] = Field(description="Документи рішення (від ЦЗО)")
    dateCreated: datetime = Field(description="Дата винесення")


class DefendantStatementDBModel(BaseModel):
    description: str = Field(description="Контраргументи / Позиція постачальника", max_length=5_000)
    documents: list[Document] = Field(description="Документи Постачальника (відповідача)")
    dateCreated: datetime = Field(description="Дата створення")


class ViolationReportDBModel(BaseModel):
    # користувацькі дані
    reason: ViolationReportReason = Field(description="Тип звернення")
    description: str = Field(description="Суть порушення")
    documents: list[Document] = Field(description="Документи Замовника (скаржника)")

    # системні поля
    id: str = Field(alias="_id", default_factory=lambda: uuid4().hex)
    rev: str = Field(alias="_rev", default="")
    tender_id: str
    contract_id: str
    dateCreated: datetime = Field(description="Дата створення")
    dateModified: datetime = Field(description="Дата оновлення")

    buyer: Buyer = Field(description="Інформація про Замовника (скаржника)")
    suppliers: list[Supplier] = Field(description="Інформація про Постачальника (відповідача)")
    procuringEntity: Optional[ProcuringEntity] = Field(None, description="Інформація про ЦЗО (власник відбору)")

    # вкладені об'єкти що додаються іншими сторонами
    defendantPeriod: Period = Field(description="Період коли відповідачу дозволено надавати пояснення")
    defendantStatement: Optional[DefendantStatementDBModel] = Field(None, description="Контраргументи Постачальника")

    decisionPeriod: Period = Field(description="Період для внесення рішення від ЦЗО")
    decision: Optional[ViolationReportDecisionDBModel] = Field(None, description="Рішення від ЦЗО")

    @computed_field
    @property
    def status(self) -> ViolationReportDecisionStatus | Literal["pending"]:
        if self.decision is None:
            return "pending"
        else:
            return self.decision.status
