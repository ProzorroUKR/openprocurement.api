from openprocurement.api.context import get_request
from openprocurement.api.procedure.models.document import ConfidentialityTypes
from openprocurement.api.procedure.serializers.document import DocumentSerializer
from openprocurement.api.procedure.utils import is_item_owner
from openprocurement.framework.core.procedure.utils import is_framework_owner


class SubmissionDocumentSerializer(DocumentSerializer):
    def __init__(self, data: dict):
        self.private_fields = set()
        super().__init__(data)
        if data.get("confidentiality", "") == ConfidentialityTypes.BUYER_ONLY:
            request = get_request()
            submission = request.validated["submission"]
            if not is_item_owner(request, submission) and not is_framework_owner(request, submission):
                self.private_fields.add("url")
