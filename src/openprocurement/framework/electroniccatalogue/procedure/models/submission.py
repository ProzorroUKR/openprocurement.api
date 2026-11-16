from openprocurement.api.constants import FrameworkType
from openprocurement.framework.core.procedure.models.submission import (
    PostSubmission as BasePostSubmission,
)
from openprocurement.framework.core.procedure.models.submission import (
    Submission as BaseSubmission,
)
from openprocurement.framework.electroniccatalogue.constants import ElectronicCatalogueFrameworkType


class PostSubmission(BasePostSubmission):
    submissionType: ElectronicCatalogueFrameworkType = FrameworkType.ELECTRONIC_CATALOGUE


class Submission(BaseSubmission):
    submissionType: ElectronicCatalogueFrameworkType = FrameworkType.ELECTRONIC_CATALOGUE
