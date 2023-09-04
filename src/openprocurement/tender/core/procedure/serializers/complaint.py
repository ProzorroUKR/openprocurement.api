from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, ListSerializer
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer
from openprocurement.tender.core.procedure.serializers.complaint_post import ComplaintPostSerializer


class ComplaintSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(ConfidentialDocumentSerializer),
        "posts": ListSerializer(ComplaintPostSerializer),
    }
    private_fields = {
        "owner",
        "owner_token",
        "transfer_token",
    }


class TenderComplaintSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(ConfidentialDocumentSerializer),
        "posts": ListSerializer(ComplaintPostSerializer),
    }

    @property
    def private_fields(self):
        base_fields = {
            "owner",
            "owner_token",
            "transfer_token",
        }
        if self._data.get("type") == "claim":
            base_fields.add("author")
        return base_fields
