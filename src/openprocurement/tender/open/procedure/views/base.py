from openprocurement.api.procedure.context import get_object


class COStateResourceMixin:
    """
    competitiveOrdering: the state depends on the agreement of the tender
    (the short procedure - an agreement with items, the long one - without)
    """

    state_class = None
    state_short_class = None
    state_long_class = None

    def __init__(self, request, context=None):
        self.state_short = self.state_short_class(request)
        self.state_long = self.state_long_class(request)
        super().__init__(request, context)

    @property
    def state(self):
        agreement = get_object("agreement")
        if agreement.get("items"):
            return self.state_short
        return self.state_long
