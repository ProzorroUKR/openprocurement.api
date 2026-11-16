from typing import Any, Literal
from uuid import uuid4

from pydantic import computed_field

from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.models.base import Model


class CreateComplaintPost(Model):
    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def datePublished(self) -> Any:
        return get_request_now().isoformat()

    @computed_field
    def author(self) -> Any:
        return self.get_author()

    @staticmethod
    def get_author():
        return get_request().authenticated_role

    title: str
    description: str
    recipient: Literal["complaint_owner", "tender_owner", "aboveThresholdReviewers"] | None = None
    relatedPost: str | None = None
    relatedObjection: str
