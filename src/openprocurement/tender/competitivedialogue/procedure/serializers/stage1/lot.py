from openprocurement.api.procedure.serializers.base import BaseSerializer


class LotStage1Serializer(BaseSerializer):
    private_fields = {
        "auctionPeriod",  # TODO: remove after refactoring (non-refactored code adds this)
    }
