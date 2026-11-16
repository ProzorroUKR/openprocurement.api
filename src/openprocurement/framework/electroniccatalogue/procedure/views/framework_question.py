from cornice.resource import resource

from openprocurement.api.constants import FrameworkType
from openprocurement.framework.core.procedure.views.question import CoreQuestionResource


@resource(
    name=f"{FrameworkType.ELECTRONIC_CATALOGUE}:Framework Questions",
    collection_path="/frameworks/{framework_id}/questions",
    path="/frameworks/{framework_id}/questions/{question_id}",
    frameworkType=FrameworkType.ELECTRONIC_CATALOGUE,
    description="Framework related questions",
)
class FrameworkQuestionsResource(CoreQuestionResource):
    pass
