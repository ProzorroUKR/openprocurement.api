import logging
from pkg_resources import get_distribution
from zope.component import queryUtility
from schematics.exceptions import ModelValidationError
from openprocurement.agreement.core.interfaces import IAgreementBuilder
from openprocurement.api.utils import (
    set_modetest_titles,
    get_revision_changes,
    apply_data_patch,
    get_now,
    context_unpack,
    generate_id
    )


PKG = get_distribution(__package__)
LOGGER = logging.getLogger(PKG.project_name)


def agreement_serialize(request, agreement_data, fields):
    configurator = request.content_configurator
    builder = queryUtility(
        IAgreementBuilder,
        name=configurator.agreement_type
        )
    agreement = builder(agreement_data)
    agreement.__parent__ = request.context
    return {
        i: j for i, j in
        agreement.serialize("view").items()
        if i in fields
        }


def save_agreement(request):
    """
    Save contract object to database
    :param request:
    :return: True if Ok
    """
    agreement = request.validated['agreement']

    if agreement.mode == u'test':
        set_modetest_titles(agreement)
    patch = get_revision_changes(
        agreement.serialize("plain"),
        request.validated['agreement_src']
        )
    if patch:
        agreement.revisions.append(
            type(agreement).revisions.model_class({
                'author': request.authenticated_userid,
                'changes': patch, 'rev': agreement.rev
            }))

        old_date_modified = agreement.dateModified
        agreement.dateModified = get_now()
        try:
            agreement.store(request.registry.db)
        except ModelValidationError as e:  # pragma: no cover
            for i in e.message:
                request.errors.add('body', i, e.message[i])
            request.errors.status = 422
        except Exception as e:  # pragma: no cover
            request.errors.add('body', 'data', str(e))
        else:
            LOGGER.info(
                'Saved agreement {}: dateModified {} -> {}'.format(
                    agreement.id, old_date_modified and old_date_modified.isoformat(),
                    agreement.dateModified.isoformat()),
                    extra=context_unpack(
                        request,
                        {'MESSAGE_ID': 'save_agreement'},
                        {'AGREEMENT_REV': agreement.rev}
                    )
            )
            return True


def apply_patch(request, data=None, save=True, src=None):
    data = request.validated['data'] if data is None else data
    patch = data and apply_data_patch(src or request.context.serialize(), data)
    if patch:
        request.context.import_data(patch)
        if save:
            return save_agreement(request)


def set_ownership(item, request):
    item.owner_token = generate_id()
