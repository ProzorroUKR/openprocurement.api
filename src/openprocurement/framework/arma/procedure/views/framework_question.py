from cornice.resource import resource

from openprocurement.framework.arma.constants import ARMA_TYPE
from openprocurement.framework.core.procedure.views.question import CoreQuestionResource


@resource(
    name=f"{ARMA_TYPE}:Framework Questions",
    collection_path="/frameworks/{framework_id}/questions",
    path="/frameworks/{framework_id}/questions/{question_id}",
    frameworkType=ARMA_TYPE,
    description="Framework related questions",
)
class FrameworkQuestionsResource(CoreQuestionResource):
    pass
