from cornice.resource import resource
from openprocurement.framework.core.procedure.views.question import CoreQuestionResource
from openprocurement.framework.dps.constants import DPS_TYPE


@resource(
    name=f"{DPS_TYPE}:Framework Questions",
    collection_path="/frameworks/{framework_id}/questions",
    path="/frameworks/{framework_id}/questions/{question_id}",
    frameworkType=DPS_TYPE,
    description="Framework related questions",
)
class FrameworkQuestionsResource(CoreQuestionResource):
    pass
