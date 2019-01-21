# -*- coding: utf-8 -*-
from openprocurement.planning.api.utils import (
    opresource,
    APIResource
)
from openprocurement.api.utils import (
    json_view
)


@opresource(name='Plan Revisions',
            collection_path='/plans/{plan_id}/revisions',
            path='/plans/{plan_id}/revisions/{revision_id}',
            description="Plan revisions")
class PlansRevisionResource(APIResource):

    @json_view(permission='revision_plan')
    def collection_get(self):
        """Plan Revisions List"""
        plan = self.request.validated['plan']
        plan_revisions = plan.serialize('revision')
        return {'data': plan_revisions}
