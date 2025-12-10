from pydantic import field_validator

from prozorro_cdb.api.database.schema.document import DocumentTypes
from prozorro_cdb.api.handlers.schema.document import PatchDocument as BasePatchDocument
from prozorro_cdb.api.handlers.schema.document import PostDocument as BasePostDocument


class PostDocument(BasePostDocument):
    @field_validator("documentType", mode="after")
    @classmethod
    def specific_doc_types(cls, value: DocumentTypes) -> DocumentTypes:
        if value not in [DocumentTypes.violationReportSignature, DocumentTypes.violationReportEvidence]:
            raise ValueError(
                f"Inapropriate documentType {value}; expected: violationReportSignature or violationReportEvidence"
            )
        return value


class PatchDocument(BasePatchDocument):
    pass
