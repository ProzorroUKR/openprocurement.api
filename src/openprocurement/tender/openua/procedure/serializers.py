from openprocurement.tender.core.procedure.serializers.bid import BidSerializer as BaseBidSerializer


class BidSerializer(BaseBidSerializer):

    def __init__(self, data: dict):
        super().__init__(data)
        if data.get("status") in ("invalid", "deleted"):
            self.whitelist = {"id", "status"}
