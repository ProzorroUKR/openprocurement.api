from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import Url


class Project(Model):
    id: str | None = None
    title: str
    uri: Url
