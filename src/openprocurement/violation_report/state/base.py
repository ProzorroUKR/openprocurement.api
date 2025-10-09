from datetime import datetime
from typing import List

from openprocurement.api.models_async.document import RequestDocument
from openprocurement.api.storage_async import upload_documents
from openprocurement.violation_report.database.schema.violation_report import Document


class BaseState:
    @staticmethod
    def create_document_objects(now: datetime, base_url: str, documents: List[RequestDocument]) -> List[Document]:
        return [
            Document.model_validate(dict(id=document_id, datePublished=now, dateModified=now, **d.model_dump()))
            for document_id, d in upload_documents(
                current_url=base_url,
                documents=documents,
            )
        ]
