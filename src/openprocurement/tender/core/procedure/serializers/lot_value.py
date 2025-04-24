from openprocurement.api.context import get_request
from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.utils import is_item_owner


class LotValueSerializer(BaseSerializer):
    private_fields: set[str] = set()

    def __init__(self, data: dict, bid=None, tender=None, **kwargs):
        super().__init__(data, **kwargs)

        # bid owner should see all fields
        if is_item_owner(get_request(), bid):
            return

        # only bid owner should see participationUrl
        self.private_fields = self.private_fields.copy()
        self.private_fields.add("participationUrl")

        # configure fields visibility
        # based on lot value, bid and tender statuses
        if (
            data.get("status") in ("unsuccessful",)
            or bid.get("status")
            in (
                "invalid",
                "invalid.pre-qualification",
                "unsuccessful",
                "deleted",
            )
            or tender.get("status")
            in (
                "active.pre-qualification",
                "active.pre-qualification.stand-still",
                "active.auction",
                "active.stage2.pending",
                "active.stage2.waiting",
            )
        ):
            self.whitelist = {
                "relatedLot",
                "status",
            }
