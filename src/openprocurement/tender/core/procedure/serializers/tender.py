from openprocurement.tender.core.procedure.serializers.base import BaseUIDSerializer, ListSerializer
from openprocurement.tender.core.procedure.serializers.bid import BidSerializer
from openprocurement.tender.core.procedure.serializers.cancellation import CancellationSerializer
from openprocurement.tender.core.procedure.serializers.complaint import ComplaintSerializer
from openprocurement.tender.core.procedure.serializers.award import AwardSerializer


class TenderBaseSerializer(BaseUIDSerializer):
    base_private_fields = {
        "dialogue_token",
        "transfer_token",
        "_rev",
        "doc_type",
        "rev",
        "owner_token",
        "revisions",
        "numberOfBids",
        "public_modified",
        "is_public",
        "is_test",
    }
    serializers = {
        "bids": ListSerializer(BidSerializer),
        "cancellations": ListSerializer(CancellationSerializer),
        "complaints": ListSerializer(ComplaintSerializer),
        "awards": ListSerializer(AwardSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)

        self.private_fields = set(self.base_private_fields)

        if data.get("status") in ("draft", "active.enquiries", "active.tendering", "active.auction"):
            self.private_fields.add("bids")

