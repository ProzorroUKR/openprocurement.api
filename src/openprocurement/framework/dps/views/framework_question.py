from openprocurement.framework.core.utils import frameworksresource
from openprocurement.framework.core.views.question import CoreQuestionResource
from openprocurement.framework.dps.constants import DPS_TYPE


@frameworksresource(
    name=f"{DPS_TYPE}:Framework Questions",
    collection_path="/frameworks/{framework_id}/questions",
    path="/frameworks/{framework_id}/questions/{question_id}",
    frameworkType=DPS_TYPE,
    description="Framework related questions",
)
class FrameworkQuestionsResource(CoreQuestionResource):
    pass
