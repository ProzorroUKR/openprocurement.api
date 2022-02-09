from openprocurement.tender.openeu.procedure.serializers.tender import TenderEUSerializer
from openprocurement.tender.core.procedure.serializers.base import ListSerializer
from openprocurement.tender.competitivedialogue.procedure.serializers.stage1.lot import LotStage1Serializer


class CD1StageTenderSerializer(TenderEUSerializer):
    serializers = TenderEUSerializer.serializers.copy()
    serializers.update(
        lots=ListSerializer(LotStage1Serializer)
    )

    def __init__(self, data: dict):
        super().__init__(data)

        self.private_fields = {
            "transfer_token",
            "_rev",
            "doc_type",
            "rev",
            "owner_token",
            "dialogue_token",
            "revisions",
            "numberOfBids",
            "auctionPeriod",  # non-refactored code adds this
        }
        if data.get("status") in ("draft", "active.tendering"):
            self.private_fields.add("bids")
