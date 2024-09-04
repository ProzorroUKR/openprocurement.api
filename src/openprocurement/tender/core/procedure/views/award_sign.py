from openprocurement.tender.core.procedure.serializers.award import AwardSerializer
from openprocurement.tender.core.procedure.views.award import resolve_award
from openprocurement.tender.core.procedure.views.sign import BaseSignResource


class AwardSignResource(BaseSignResource):
    serializer_class = AwardSerializer
    obj_name = "award"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_award(request)
