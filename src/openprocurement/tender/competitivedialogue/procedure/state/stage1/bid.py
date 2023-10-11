# -*- coding: utf-8 -*-
from openprocurement.tender.core.procedure.state.bid import BidState as BaseBidState


class CDStage1BidState(BaseBidState):
    update_date_on_value_amount_change_enabled = False
