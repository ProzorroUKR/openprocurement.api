from typing import Any
from uuid import uuid4

from pydantic import Field, computed_field

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.tender.core.procedure.models.criterion import LegislationItem
from openprocurement.tender.core.procedure.models.document import Document, PostDocument


class Proceeding(Model):
    dateProceedings: IsoDateTime
    proceedingNumber: str


class PostAppeal(Model):
    description: str
    documents: list[PostDocument] | None = None

    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def dateCreated(self) -> Any:
        return get_request_now().isoformat()

    @computed_field
    def datePublished(self) -> Any:
        return get_request_now().isoformat()

    @computed_field
    def legislation(self) -> Any:
        legislation = {
            "version": "2020-04-19",
            "type": "NATIONAL_LEGISLATION",
            "article": "18.23",
            "identifier": {
                "id": "922-VIII",
                "legalName": 'Закон України "Про публічні закупівлі"',
                "uri": "https://zakon.rada.gov.ua/laws/show/922-19#n1284",
            },
        }
        return legislation


class PatchAppeal(Model):
    proceeding: Proceeding | None = None


class Appeal(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    description: str | None = None
    documents: list[Document] | None = None
    proceeding: Proceeding | None = None
    legislation: LegislationItem | None = None
    author: str | None = None
    dateCreated: IsoDateTime | None = None
    datePublished: IsoDateTime | None = None
