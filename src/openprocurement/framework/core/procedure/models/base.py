from pydantic import computed_field

from openprocurement.api.procedure.models.base import RootModel


class FrameworkRootModel(RootModel):
    """A database document of the framework domain"""

    @computed_field(alias="id")
    def doc_id(self) -> str | None:
        """the database document of the framework domain has its id next to `_id`"""
        return self.id
