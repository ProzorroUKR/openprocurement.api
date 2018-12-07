from string import hexdigits
from urlparse import parse_qs, urlparse

from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.core.models import Document
from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.serializable import serializable


class EUDocument(Document):
    class Options:
        namespace = 'document'
        roles = RolesFromCsv('EUDocument.csv', relative_to=__file__)

    language = StringType(required=True, choices=['uk', 'en', 'ru'], default='uk')


class BidderEUDocument(EUDocument):
    """ Confidential Document """
    class Options:
        roles = RolesFromCsv('BidderEUDocument.csv', relative_to=__file__)
    confidentiality = StringType(choices=['public', 'buyerOnly'], default='public')
    confidentialityRationale = StringType()

    documentType = StringType(choices=[
        'tenderNotice', 'awardNotice', 'contractNotice', 'notice', 'biddingDocuments', 'technicalSpecifications',
        'evaluationCriteria', 'clarifications', 'shortlistedFirms', 'riskProvisions', 'billOfQuantity', 'bidders',
        'conflictOfInterest', 'debarments', 'evaluationReports', 'winningBid', 'complaints', 'contractSigned',
        'contractArrangements', 'contractSchedule', 'contractAnnexe', 'contractGuarantees', 'subContract',
        'eligibilityCriteria', 'contractProforma', 'commercialProposal', 'qualificationDocuments',
        'eligibilityDocuments', 'registerExtract', 'winningBid'
    ])

    def validate_confidentialityRationale(self, data, val):
        if data['confidentiality'] != 'public':
            if not val:
                raise ValidationError(u"confidentialityRationale is required")
            elif len(val) < 30:
                raise ValidationError(u"confidentialityRationale should contain at least 30 characters")

    @serializable(serialized_name="url")
    def download_url(self):
        url = self.url
        if self.confidentiality == 'buyerOnly':
            return self.url
        if not url or '?download=' not in url:
            return url
        doc_id = parse_qs(urlparse(url).query)['download'][-1]
        root = self.__parent__
        parents = []
        while root.__parent__ is not None:
            parents[0:0] = [root]
            root = root.__parent__
        request = root.request
        if not request.registry.docservice_url:
            return url
        if 'status' in parents[0] and parents[0].status in type(parents[0])._options.roles:
            role = parents[0].status
            for index, obj in enumerate(parents):
                if obj.id != url.split('/')[(index - len(parents)) * 2 - 1]:
                    break
                field = url.split('/')[(index - len(parents)) * 2]
                if "_" in field:
                    field = field[0] + field.title().replace("_", "")[1:]
                roles = type(obj)._options.roles
                if roles[role if role in roles else 'default'](field, []):
                    return url
        from openprocurement.api.utils import generate_docservice_url
        if not self.hash:
            path = [i for i in urlparse(url).path.split('/') if len(i) == 32 and not set(i).difference(hexdigits)]
            return generate_docservice_url(request, doc_id, False, '{}/{}'.format(path[0], path[-1]))
        return generate_docservice_url(request, doc_id, False)
