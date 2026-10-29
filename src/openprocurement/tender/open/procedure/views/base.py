from openprocurement.api.procedure.context import get_object
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.open.constants import OPEN_TENDERING_EU
from openprocurement.tender.open.procedure.utils import get_open_tendering_variant


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


class OpenTenderingStateClass:
    """
    openTendering state class resolver for state_classes: the state depends on the UA/EU variant of the tender
    set by its procedure.euPublished field (POST /tenders: read from the request body, otherwise from the tender)
    """

    def __init__(self, ua_state_class, eu_state_class):
        self.ua_state_class = ua_state_class
        self.eu_state_class = eu_state_class

    def __call__(self, request):
        tender = request.validated.get("tender")
        if not tender:
            # POST /tenders: the body is already parsed by the route predicate (validate_json_data)
            tender = request.validated.get("json_data")
        # a missing/invalid value is rejected by the post data model and the procedure schema (the UA state does it)
        if get_open_tendering_variant(tender) == OPEN_TENDERING_EU:
            return self.eu_state_class
        return self.ua_state_class
