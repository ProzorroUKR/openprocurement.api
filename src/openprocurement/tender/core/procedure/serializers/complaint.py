from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.tender.core.procedure.serializers.complaint_objection import (
    ComplaintObjectionSerializer,
)
from openprocurement.tender.core.procedure.serializers.complaint_post import (
    ComplaintPostSerializer,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)


class ComplaintSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
        "posts": ListSerializer(ComplaintPostSerializer),
        "objections": ListSerializer(ComplaintObjectionSerializer),
    }
    private_fields = {
        "owner",
        "owner_token",
        "transfer_token",
    }


class TenderComplaintSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
        "posts": ListSerializer(ComplaintPostSerializer),
        "objections": ListSerializer(ComplaintObjectionSerializer),
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
