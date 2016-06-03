# -*- coding: utf-8 -*-
from datetime import timedelta
from schematics.types import StringType
from schematics.exceptions import ValidationError
from zope.interface import implementer
from schematics.types.serializable import serializable
from schematics.types.compound import ModelType
from openprocurement.api.models import ITender, get_now
from openprocurement.tender.openua.models import Tender as TenderUA
from openprocurement.tender.openeu.models import Tender as TenderEU
from openprocurement.tender.openeu.models import (TENDERING_DAYS, TENDERING_DURATION,
                                                  QUESTIONS_STAND_STILL, COMPLAINT_STAND_STILL,
                                                  EnquiryPeriod, ENQUIRY_STAND_STILL_TIME)
from openprocurement.tender.openua.utils import calculate_business_date
from openprocurement.api.models import (
    plain_role, create_role, edit_role, view_role, listing_role,
    auction_view_role, auction_post_role, auction_patch_role, enquiries_role,
    auction_role, chronograph_role, chronograph_view_role, view_bid_role,
    Administrator_bid_role, Administrator_role, schematics_default_role,
    TZ, get_now, schematics_embedded_role, validate_lots_uniq, draft_role,
    embedded_lot_role, default_lot_role, calc_auction_end_time, get_tender,
    ComplaintModelType, validate_cpv_group, validate_items_uniq, Model,
)
from openprocurement.tender.openeu.models import Document
from schematics.transforms import whitelist, blacklist
edit_role_ua = edit_role + blacklist('enquiryPeriod', 'status')

roles = {
    'plain': plain_role,
    'create': create_role,
    'edit': edit_role_ua,
    'edit_draft': draft_role,
    'edit_active.tendering': edit_role_ua,
    'edit_active.qualification': whitelist(),
    'edit_active.awarded': whitelist(),
    'edit_complete': whitelist(),
    'edit_unsuccessful': whitelist(),
    'edit_cancelled': whitelist(),
    'view': view_role,
    'listing': listing_role,
    'draft': enquiries_role,
    'active.tendering': enquiries_role,
    'active.qualification': view_role,
    'active.awarded': view_role,
    'complete': view_role,
    'unsuccessful': view_role,
    'cancelled': view_role,
    'chronograph': chronograph_role,
    'chronograph_view': chronograph_view_role,
    'Administrator': Administrator_role,
    'default': schematics_default_role,
    'contracting': whitelist('doc_id', 'owner'),
    }


@implementer(ITender)
class Tender(TenderUA):
    procurementMethodType = StringType(default="competitiveDialogue.aboveThresholdUA")
    status = StringType(choices=['draft', 'active.tendering', 'active.pre-qualification',
                                 'active.pre-qualification.stand-still', 'active.qualification',
                                 'active.awarded', 'complete', 'cancelled', 'unsuccessful'],
                        default='active.tendering')
    auctionPeriod = None  # We don't need this field more

    class Options:
        roles = roles.copy()

    def validate_tenderPeriod(self, data, period):
        # if data['_rev'] is None when tender was created just now
        if not data['_rev'] and calculate_business_date(get_now(), -timedelta(minutes=10)) >= period.startDate:
            raise ValidationError(u"tenderPeriod.startDate should be in greater than current date")
        if period and calculate_business_date(period.startDate, TENDERING_DURATION, data) > period.endDate:
            raise ValidationError(u"tenderPeriod should be greater than {} days".format(TENDERING_DAYS))


CompetitiveDialogUA = Tender


@implementer(ITender)
class Tender(TenderEU):
    procurementMethodType = StringType(default="competitiveDialogue.aboveThresholdEU")
    status = StringType(choices=['draft', 'active.tendering', 'active.pre-qualification',
                                 'active.pre-qualification.stand-still', 'active.qualification',
                                 'active.awarded', 'complete', 'cancelled', 'unsuccessful'],
                        default='active.tendering')
    auctionPeriod = None  # We don't need this field more

    class Options:
        roles = roles.copy()


CompetitiveDialogEU = Tender


class DescriptionDocument(Document):
    """ Description of the decision to purchase """

    class Options:
        roles = {
            'edit': blacklist('id', 'url', 'datePublished', 'dateModified', ''),
            'embedded': schematics_embedded_role,
            'view': (blacklist('revisions') + schematics_default_role),
            'restricted_view': (blacklist('revisions', 'url') + schematics_default_role),
            'revisions': whitelist('url', 'dateModified'),
        }

    confidentiality = StringType(choices=['public', 'buyerOnly'], default='public')
