from openprocurement.framework.core.utils import frameworksresource
from openprocurement.framework.core.views.question import CoreQuestionResource
from openprocurement.framework.electroniccatalogue.constants import ELECTRONIC_CATALOGUE_TYPE


@frameworksresource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Framework Questions",
    collection_path="/frameworks/{framework_id}/questions",
    path="/frameworks/{framework_id}/questions/{question_id}",
    frameworkType=ELECTRONIC_CATALOGUE_TYPE,
    description="Framework related questions",
)
class FrameworkQuestionsResource(CoreQuestionResource):
    pass
