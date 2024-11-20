from cornice.resource import resource

from openprocurement.framework.core.procedure.views.question import CoreQuestionResource
from openprocurement.framework.ifi.constants import IFI_TYPE


@resource(
    name=f"{IFI_TYPE}:Framework Questions",
    collection_path="/frameworks/{framework_id}/questions",
    path="/frameworks/{framework_id}/questions/{question_id}",
    frameworkType=IFI_TYPE,
    description="Framework related questions",
)
class FrameworkQuestionsResource(CoreQuestionResource):
    pass
