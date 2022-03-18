from openprocurement.tender.openeu.procedure.serializers.bid import BidSerializer
from openprocurement.tender.core.procedure.serializers.qualification import QualificationSerializer
from openprocurement.tender.core.procedure.serializers.base import ListSerializer
from openprocurement.tender.core.procedure.serializers.tender import TenderBaseSerializer
from openprocurement.tender.core.procedure.serializers.award import AwardSerializer
from openprocurement.tender.core.procedure.serializers.cancellation import CancellationSerializer
from openprocurement.tender.core.procedure.serializers.complaint import ComplaintSerializer


class TenderEUSerializer(TenderBaseSerializer):
    serializers = {
        "bids": ListSerializer(BidSerializer),
        "qualifications": ListSerializer(QualificationSerializer),
        "cancellations": ListSerializer(CancellationSerializer),
        "complaints": ListSerializer(ComplaintSerializer),
        "awards": ListSerializer(AwardSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)

        self.private_fields = {
            "dialogue_token",
            "transfer_token",
            "_rev",
            "doc_type",
            "rev",
            "owner_token",
            "revisions",
            "numberOfBids",
        }
        if data.get("status") in ("draft", "active.tendering"):
            self.private_fields.add("bids")
