from openprocurement.api.procedure.models.document import ConfidentialityType
from openprocurement.api.procedure.serializers.document import (
    DocumentSerializer as BaseDocumentSerializer,
)
from openprocurement.api.procedure.utils import is_item_owner
from openprocurement.tender.core.procedure.context import get_request


class DocumentSerializer(BaseDocumentSerializer):
    def __init__(self, data: dict):
        self.private_fields = set()
        super().__init__(data)
        if data.get("confidentiality", "") == ConfidentialityType.BUYER_ONLY:
            request = get_request()
            if (
                request.authenticated_role not in ("aboveThresholdReviewers", "sas")
                and not ("bid" in request.validated and is_item_owner(request, request.validated["bid"]))
                and not is_item_owner(request, request.validated["tender"])
            ):
                self.private_fields.add("url")
