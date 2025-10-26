from datetime import datetime
from typing import List

from prozorro_cdb.api.database.schema.document import Document
from prozorro_cdb.api.handlers.schema.document import PostDocument
from prozorro_cdb.api.storage import upload_documents


class BaseState:
    @staticmethod
    def create_document_objects(now: datetime, base_url: str, documents: List[PostDocument]) -> List[Document]:
        return [
            Document.model_validate(dict(id=document_id, datePublished=now, dateModified=now, **d.model_dump()))
            for document_id, d in upload_documents(
                current_url=base_url,
                documents=documents,
            )
        ]
