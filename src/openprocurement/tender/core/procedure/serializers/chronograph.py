from openprocurement.api.procedure.serializers.base import BaseUIDSerializer


class ChronographSerializer(BaseUIDSerializer):
    def __init__(self, data: dict):
        super().__init__(data)

        self.whitelist = {
            "id",
            "status",
            "enquiryPeriod",
            "tenderPeriod",
            "auctionPeriod",
            "awardPeriod",
            "awards",
            "lots",
            "doc_id",
            "submissionMethodDetails",
            "mode",
            "date",
            "numberOfBids",
            "complaints",
            "qualifications",
            "contracts",
            "next_check",
        }
