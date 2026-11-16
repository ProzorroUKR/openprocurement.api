from cornice.resource import resource

from openprocurement.api.constants import FrameworkType
from openprocurement.framework.core.procedure.views.question import CoreQuestionResource


@resource(
    name=f"{FrameworkType.DYNAMIC_PURCHASING_SYSTEM}:Framework Questions",
    collection_path="/frameworks/{framework_id}/questions",
    path="/frameworks/{framework_id}/questions/{question_id}",
    frameworkType=FrameworkType.DYNAMIC_PURCHASING_SYSTEM,
    description="Framework related questions",
)
class FrameworkQuestionsResource(CoreQuestionResource):
    pass
