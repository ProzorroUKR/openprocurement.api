from datetime import datetime
from enum import StrEnum
from typing import Literal, Optional
from uuid import uuid4

from pydantic import Field

from prozorro_cdb.api.database.schema.common import BaseModel, Period
from prozorro_cdb.api.database.schema.document import Document
from prozorro_cdb.api.database.schema.organization import (
    Buyer,
    ProcuringEntity,
    Supplier,
)


class ViolationReportReason(StrEnum):
    goodsNonCompliance = "goodsNonCompliance"
    contractBreach = "contractBreach"
    signingRefusal = "signingRefusal"


class ViolationReportResolution(StrEnum):
    satisfied = "satisfied"
    declinedNoViolation = "declinedNoViolation"
    declinedLackEvidence = "declinedLackEvidence"


class DraftActiveObjectStatus(StrEnum):
    draft = "draft"
    active = "active"


class DecisionDBModel(BaseModel):
    id: str
    resolution: ViolationReportResolution
    description: str = Field(description="Опис рішення", max_length=5_000)
    documents: list[Document] = Field(default_factory=list, description="Документи рішення (від ЦЗО)")
    dateModified: datetime = Field(description="Дата оновлення")
    datePublished: Optional[datetime] = Field(default=None, description="Дата публікації")
    status: DraftActiveObjectStatus = Field(default=DraftActiveObjectStatus.draft)


class DefendantStatementDBModel(BaseModel):
    id: str
    description: str = Field(description="Контраргументи / Позиція постачальника", max_length=5_000)
    documents: list[Document] = Field(default_factory=list, description="Документи Постачальника (відповідача)")
    dateModified: datetime = Field(description="Дата оновлення")
    datePublished: Optional[datetime] = Field(default=None, description="Дата публікації")
    status: DraftActiveObjectStatus = Field(default=DraftActiveObjectStatus.draft)


class ReportDetails(BaseModel):
    reason: ViolationReportReason = Field(description="Тип звернення")
    description: str = Field(description="Суть порушення")
    documents: list[Document] = Field(description="Документи Замовника (скаржника)")
    dateModified: datetime = Field(description="Дата оновлення")


class ViolationReportStatus(StrEnum):
    draft = "draft"
    pending = "pending"
    satisfied = "satisfied"
    declinedNoViolation = "declinedNoViolation"
    declinedLackEvidence = "declinedLackEvidence"


class ViolationReportDBModel(BaseModel):
    # користувацькі дані
    details: ReportDetails

    # системні поля
    id: str = Field(alias="_id", default_factory=lambda: uuid4().hex)
    rev: str = Field(alias="_rev", default="")
    status: ViolationReportStatus = Field(default=ViolationReportStatus.draft)
    mode: Optional[Literal["test"]] = Field(None, description="Тест мод (з тендера)")
    tender_id: str
    contract_id: str
    dateCreated: datetime = Field(description="Дата створення")
    dateModified: datetime = Field(description="Дата оновлення")
    datePublished: Optional[datetime] = Field(None, description="Дата публікації")

    author: Buyer = Field(description="Інформація про Замовника (скаржника)")
    defendants: list[Supplier] = Field(min_length=1, description="Інформація про Постачальника (відповідача)")
    authority: ProcuringEntity = Field(None, description="Інформація про ЦЗО (власник відбору)")

    # вкладені об'єкти що додаються іншими сторонами
    defendantPeriod: Optional[Period] = Field(None, description="Період коли відповідачу дозволено надавати пояснення")
    defendantStatements: list[DefendantStatementDBModel] = Field(
        default_factory=list, description="Контраргументи Постачальника"
    )

    decisions: list[DecisionDBModel] = Field(default_factory=list, description="Рішення ЦЗО")
