from openprocurement.api.procedure.serializers.base import (
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.planning.api.procedure.serializers.milestone import (
    MilestoneSerializer,
)


class PlanSerializer(BaseUIDSerializer):
    base_private_fields = {
        "transfer_token",
        "_rev",
        "doc_type",
        "rev",
        "owner_token",
        "revisions",
        "public_modified",
        "is_public",
        "is_test",
    }
    serializers = {
        "milestones": ListSerializer(MilestoneSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)

    @property
    def data(self) -> dict:
        data = super().data

        # default value, for plans before statuses released
        if data.get("status") is None:
            if data.get("tender_id") is None:
                data["status"] = "scheduled"
            else:
                data["status"] = "complete"

        return data


class PlanRevisionsSerializer(BaseUIDSerializer):
    whitelist = (
        "_id",
        "revisions",
    )
