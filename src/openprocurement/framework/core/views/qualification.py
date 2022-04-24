from openprocurement.api.utils import MongodbResourceListing
from openprocurement.framework.core.utils import qualificationsresource


@qualificationsresource(
    name="Qualifications",
    path="/qualifications",
    description="",  # TODO: Add description
)
class QualificationResource(MongodbResourceListing):
    def __init__(self, request, context):
        super().__init__(request, context)
        self.listing_name = "Qualifications"
        self.listing_default_fields = {"dateModified"}
        self.all_fields = {"dateCreated", "dateModified", "id", "frameworkID", "submissionID", "status",
                           "documents", "date"}
        self.db_listing_method = request.registry.mongodb.qualifications.list
