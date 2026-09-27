from openprocurement.api.procedure.context import get_object
from openprocurement.api.utils import raise_operation_error


class COStateClass:
    """
    competitiveOrdering state class resolver for state_classes: the state depends on the agreement
    of the tender (the short procedure - an agreement with items, the long one - without)
    """

    def __init__(self, short_state_class, long_state_class):
        self.short_state_class = short_state_class
        self.long_state_class = long_state_class

    def __call__(self, request):
        agreement = get_object("agreement")
        if not agreement:
            if "tender" not in request.validated or request.method in ("GET", "HEAD"):
                # POST /tenders: the agreement is fetched later; GET: the agreement isn't fetched at all
                return self.long_state_class
            raise_operation_error(request, "Agreement not provided or not exist", status=422, name="agreements")
        if agreement.get("items"):
            return self.short_state_class
        return self.long_state_class
