from typing import Any

from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.tender.core.procedure.models.req_response import (
    get_requirement_obj,
)


class RequirementResponseSerializer(BaseSerializer):

    def serialize(self, data: dict[str, Any], **kwargs) -> dict[str, Any]:
        fields_from_requirement = {"unit", "classification", "title"}
        tender = kwargs["tender"]
        kwargs["requirementResponse"] = self.raw
        requirement_id = data["requirement"]["id"]

        data = data.copy()
        requirement, _, criterion = get_requirement_obj(requirement_id, tender)
        if requirement:
            requirement = requirement.copy()
            requirement["classification"] = criterion.get("classification")

            for field in fields_from_requirement:
                if requirement.get(field):
                    if field == "title":
                        data["requirement"]["title"] = requirement[field]
                    else:
                        data[field] = requirement[field]

        return super().serialize(data, **kwargs)
