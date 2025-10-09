from typing import Literal

from openprocurement.api.models_async.document import DocumentTypes
from openprocurement.api.models_async.document import RequestDocument as BaseDocument


class RequestDocument(BaseDocument):
    documentType: Literal[DocumentTypes.violationReportSignature, DocumentTypes.violationReportEvidence]
