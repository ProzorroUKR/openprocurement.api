from typing import Any

from openprocurement.api.context import get_request
from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.api.procedure.utils import is_item_owner
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)
from openprocurement.tender.core.procedure.serializers.item import (
    ItemPreQualificationSerializer,
)
from openprocurement.tender.core.procedure.serializers.lot_value import (
    LotValueSerializer,
)
from openprocurement.tender.core.procedure.serializers.req_response import (
    RequirementResponseSerializer,
)


class BidSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
        "eligibilityDocuments": ListSerializer(DocumentSerializer),
        "financialDocuments": ListSerializer(DocumentSerializer),
        "qualificationDocuments": ListSerializer(DocumentSerializer),
        "lotValues": ListSerializer(LotValueSerializer),
        "requirementResponses": ListSerializer(RequirementResponseSerializer),
    }
    private_fields = {
        "owner",
        "owner_token",
        "transfer_token",
    }

    def serialize(self, data: dict[str, Any], **kwargs) -> dict[str, Any]:
        kwargs["bid"] = self.raw
        return super().serialize(data, **kwargs)

    def __init__(self, data: dict, tender=None, **kwargs):
        super().__init__(data, tender=tender, **kwargs)

        # bid owner should see all fields
        if is_item_owner(get_request(), data):
            return

        # only bid owner should see participationUrl
        self.private_fields = self.private_fields.copy()
        self.private_fields.add("participationUrl")

        # copy serializers to change them later
        self.serializers = self.serializers.copy()

        # configure fields visibility
        if tender["config"]["hasPrequalification"]:
            # pre-qualification rules
            self.set_tender_with_pre_qualification_whitelist(data, tender)
        else:
            # no pre-qualification rules
            self.set_tender_without_pre_qualification_whitelist(data)

    def set_tender_without_pre_qualification_whitelist(self, data):
        if data.get("status") in ("invalid", "deleted"):
            self.whitelist = {
                "id",
                "status",
                "lotValues",
            }

    def set_tender_with_pre_qualification_whitelist(self, data, tender):
        bid_status = self.serialize_status(tender, data)

        if bid_status in ("invalid", "deleted"):
            self.whitelist = {
                "id",
                "status",
                "lotValues",
            }
        elif bid_status == "invalid.pre-qualification":
            self.whitelist = {
                "id",
                "status",
                "documents",
                "eligibilityDocuments",
                "tenderers",
                "requirementResponses",
                "lotValues",
            }
        elif bid_status == "unsuccessful":
            self.whitelist = {
                "id",
                "status",
                "tenderers",
                "documents",
                "eligibilityDocuments",
                "parameters",
                "selfQualified",
                "selfEligible",
                "subcontractingDetails",
                "requirementResponses",
                "lotValues",
            }
        elif tender["status"] in (
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.auction",
            "active.stage2.pending",
            "active.stage2.waiting",
        ):
            self.whitelist = {
                "id",
                "status",
                "documents",
                "eligibilityDocuments",
                "tenderers",
                "requirementResponses",
                "items",
                "lotValues",
            }
            self.serializers["items"] = ListSerializer(ItemPreQualificationSerializer)

    def serialize_status(self, tender, bid):
        # TODO: get rid of this function
        if bid["status"] in (
            "draft",
            "invalid",
            "invalid.pre-qualification",
            "unsuccessful",
            "deleted",
        ):
            return bid["status"]

        if not tender.get("lots"):
            return bid["status"]

        if tender["status"] in ("active.tendering", "cancelled"):
            return bid["status"]

        if not bid.get("lotValues"):
            return "invalid"

        active_lots_ids = set()
        for lot in tender["lots"]:
            if lot["status"] in ("active", "complete"):
                active_lots_ids.add(lot["id"])

        lot_values_statuses = set()
        for lot_value in bid["lotValues"]:
            if lot_value["relatedLot"] in active_lots_ids:
                lot_values_statuses.add(lot_value["status"])

        if "pending" in lot_values_statuses:
            return "pending"

        if "active" in lot_values_statuses:
            return "active"

        return "unsuccessful"
