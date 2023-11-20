from cornice.resource import resource
from openprocurement.framework.core.procedure.views.question import CoreQuestionResource
from openprocurement.framework.electroniccatalogue.constants import ELECTRONIC_CATALOGUE_TYPE


@resource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Framework Questions",
    collection_path="/frameworks/{framework_id}/questions",
    path="/frameworks/{framework_id}/questions/{question_id}",
    frameworkType=ELECTRONIC_CATALOGUE_TYPE,
    description="Framework related questions",
)
class FrameworkQuestionsResource(CoreQuestionResource):
    pass
