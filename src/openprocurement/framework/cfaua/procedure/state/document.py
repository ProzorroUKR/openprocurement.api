from openprocurement.api.procedure.state.base import BaseState
from openprocurement.framework.cfaua.procedure.validation import validate_related_item
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing


class AgreementDocumentState(BaseDocumentStateMixing, BaseState):
    item_name = "agreement"

    def validate_document_post(self, data):
        validate_related_item(data.get("relatedItem"), data["documentOf"])

    def validate_document_patch(self, before, after):
        validate_related_item(after.get("relatedItem"), after["documentOf"])
