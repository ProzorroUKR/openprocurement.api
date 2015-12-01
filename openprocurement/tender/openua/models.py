# -*- coding: utf-8 -*-
from zope.interface import implementer
from schematics.types import IntType, StringType
from schematics.types.compound import ModelType, ListType
from schematics.transforms import whitelist
from openprocurement.api.models import Tender as BaseTender
from openprocurement.api.models import Bid as BaseBid
from openprocurement.api.models import (
    plain_role, create_role, edit_role, cancel_role, view_role, listing_role,
    auction_view_role, auction_post_role, auction_patch_role, enquiries_role,
    auction_role, chronograph_role, chronograph_view_role,
    Administrator_role, schematics_default_role)
from openprocurement.tender.openua.interfaces import ITenderUA


class Bid(BaseBid):
    status = StringType(choices=['registration', 'validBid', 'invalidBid', 'deleted'], default='registration')


@implementer(ITenderUA)
class Tender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""

    class Options:
        roles = {
            'plain': plain_role,
            'create': create_role,
            'edit': edit_role,
            'edit_active.enquiries': edit_role,
            'edit_active.tendering': edit_role,
            'edit_active.auction': cancel_role,
            'edit_active.qualification': cancel_role,
            'edit_active.awarded': cancel_role,
            'edit_complete': whitelist(),
            'edit_unsuccessful': whitelist(),
            'edit_cancelled': whitelist(),
            'view': view_role,
            'listing': listing_role,
            'auction_view': auction_view_role,
            'auction_post': auction_post_role,
            'auction_patch': auction_patch_role,
            'active.enquiries': enquiries_role,
            'active.tendering': enquiries_role,
            'active.auction': auction_role,
            'active.qualification': view_role,
            'active.awarded': view_role,
            'complete': view_role,
            'unsuccessful': view_role,
            'cancelled': view_role,
            'chronograph': chronograph_role,
            'chronograph_view': chronograph_view_role,
            'Administrator': Administrator_role,
            'default': schematics_default_role,
        }

    __name__ = ''

    bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the tender.
    procurementMethodType = StringType(default="aboveThresholdUA")
    magicUnicorns = IntType(required=True)
