from openprocurement.api.procedure.models.base import Model


class Reference(Model):
    id: str
    title: str | None = None


class RequirementReference(Model):
    id: str
