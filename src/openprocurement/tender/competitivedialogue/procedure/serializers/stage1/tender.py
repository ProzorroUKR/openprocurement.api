from openprocurement.api.procedure.serializers.base import ListSerializer
from openprocurement.tender.competitivedialogue.procedure.serializers.stage1.lot import (
    LotStage1Serializer,
)
from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)


class CD1StageTenderSerializer(TenderBaseSerializer):
    serializers = TenderBaseSerializer.serializers.copy()
    serializers.update(
        lots=ListSerializer(LotStage1Serializer)  # TODO: remove after refactoring (non-refactored code adds this)
    )

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = self.private_fields | {
            "auctionPeriod"  # TODO: remove after refactoring (non-refactored code adds this)
        }
