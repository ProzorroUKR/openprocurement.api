from openprocurement.tender.core.procedure.context import get_tender, get_request
from openprocurement.tender.core.procedure.serializers.base import BaseSerializer


class QuestionSerializer(BaseSerializer):
    serializers = {}

    def __init__(self, data: dict):
        super().__init__(data)
        if get_request().method != "POST" and get_tender().get("status") in (
            "active.enquiries",
            "active.tendering",
            "active.auction",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
        ):
            self.private_fields = {"author"}
