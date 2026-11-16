from cornice.resource import resource

from openprocurement.api.constants import FrameworkType
from openprocurement.framework.core.procedure.views.question import CoreQuestionResource


@resource(
    name=f"{FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS}:Framework Questions",
    collection_path="/frameworks/{framework_id}/questions",
    path="/frameworks/{framework_id}/questions/{question_id}",
    frameworkType=FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS,
    description="Framework related questions",
)
class FrameworkQuestionsResource(CoreQuestionResource):
    pass
