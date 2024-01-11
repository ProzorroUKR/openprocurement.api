from openprocurement.api.procedure.context import init_object
from openprocurement.api.views.base import BaseResource
from openprocurement.api.utils import context_unpack
from openprocurement.framework.core.procedure.models.document import Document
from openprocurement.framework.core.procedure.serializers.agreement import AgreementConfigSerializer
from openprocurement.framework.core.procedure.serializers.framework import FrameworkConfigSerializer
from openprocurement.framework.core.procedure.serializers.qualification import QualificationConfigSerializer
from openprocurement.framework.core.procedure.serializers.submission import SubmissionConfigSerializer
from openprocurement.framework.core.procedure.state.document import BaseFrameworkDocumentState
from openprocurement.framework.core.procedure.state.framework import FrameworkState
from openprocurement.tender.core.procedure.serializers.document import DocumentSerializer
from openprocurement.tender.core.procedure.views.document import DocumentResourceMixin, resolve_document
from openprocurement.tender.core.procedure.documents import get_file
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.framework.core.utils import get_framework_by_id
from openprocurement.api.database import atomic_transaction
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS


class FrameworkBaseResource(BaseResource):  # TODO: make more specific classes

    state_class = FrameworkState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_framework"),
            (Allow, "g:brokers", "create_framework"),
            (Allow, "g:framework_owner", "edit_framework"),
            (Allow, "g:brokers", "edit_framework"),
            (Allow, "g:Administrator", "edit_framework"),
            (Allow, "g:chronograph", "edit_framework"),

            # Submission permissions
            (Allow, "g:brokers", "create_submission"),
            (Allow, "g:chronograph", "edit_submission"),
            (Allow, "g:submission_owner", "edit_submission"),
            (Allow, "g:brokers", "edit_submission"),
            (Allow, "g:Administrator", "edit_submission"),

            # Qualification permissions
            (Allow, Everyone, "view_qualification"),
            (Allow, "g:bots", "create_qualification"),
            (Allow, "g:bots", "edit_qualification"),
            (Allow, "g:framework_owner", "edit_qualification"),
            (Allow, "g:brokers", "edit_qualification"),
            (Allow, "g:Administrator", "edit_qualification"),

            # Agreement permissions
            (Allow, "g:agreements", "create_agreement"),
            (Allow, "g:chronograph", "edit_agreement"),
            (Allow, "g:Administrator", "edit_agreement"),
            (Allow, "g:brokers", "edit_agreement"),

            # Question permissions
            (Allow, "g:brokers", "create_question"),
            (Allow, "g:brokers", "edit_question"),

            (Allow, "g:admins", ALL_PERMISSIONS),
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)
        # init state class that handles framework business logic
        self.state = self.state_class(request)

        # https://github.com/Cornices/cornice/issues/479#issuecomment-388407385
        # init is called twice (with and without context), thanks to cornice.
        if not context:
            # getting framework, submission, qualification, agreement
            match_dict = request.matchdict
            if match_dict:
                self.get_object_data_and_config(
                    request,
                    match_dict,
                    obj_name="framework",
                    config_serializer=FrameworkConfigSerializer,
                )
                self.get_object_data_and_config(
                    request,
                    match_dict,
                    obj_name="submission",
                    config_serializer=SubmissionConfigSerializer,
                )
                self.get_object_data_and_config(
                    request,
                    match_dict,
                    obj_name="qualification",
                    config_serializer=QualificationConfigSerializer,
                )
                self.get_object_data_and_config(
                    request,
                    match_dict,
                    obj_name="agreement",
                    config_serializer=AgreementConfigSerializer,
                )

    def get_object_data_and_config(self, request, match_dict, obj_name="framework", config_serializer=None):
        if match_dict.get(f"{obj_name}_id"):
            init_object(
                obj_name,
                getattr(request, f"{obj_name}_doc"),
                config_serializer=config_serializer,
            )
            if "frameworkID" in request.validated[obj_name]:
                framework_doc = get_framework_by_id(request, request.validated[obj_name].get("frameworkID"))
                model = request.framework_from_data(framework_doc, create=False)
                framework = model(framework_doc)
                init_object(
                    "framework",
                    framework.serialize(),
                    config_serializer=FrameworkConfigSerializer,
                )

    def save_all_objects(self):
        logger = self.LOGGER
        request = self.request

        with atomic_transaction():
            # create or update agreement
            if request.validated.get("agreement"):  # may not be created yet
                if request.validated["agreement_src"]:  # update
                    if save_object(request, "agreement", raise_error_handler=True):
                        logger.info(
                            f"Updated agreement {request.validated['agreement']['_id']} contracts",
                            extra=context_unpack(
                                request,
                                {"MESSAGE_ID": "agreement_patch"},
                            ),
                        )
                else:  # create
                    if save_object(request, "agreement", insert=True, raise_error_handler=True):
                        agreement_id = request.validated['framework'].get('agreementID')
                        logger.info(
                            f"Created agreement {agreement_id}",
                            extra=context_unpack(
                                request,
                                {"MESSAGE_ID": "agreement_create"},
                                {
                                    "agreement_id": agreement_id,
                                    "agreement_mode": request.validated['agreement'].get('mode')
                                },
                            ),
                        )

            # update framework
            if save_object(request, "framework", raise_error_handler=True):
                logger.info(
                    f"Updated framework {request.validated['framework']['_id']} with agreementID",
                    extra=context_unpack(request, {"MESSAGE_ID": "framework_patch"}),
                )

            # create or update framework
            if request.validated.get("qualification"):  # may not be created yet
                if request.validated["qualification_src"]:
                    if save_object(request, "qualification", raise_error_handler=True):
                        logger.info(
                            f"Updated qualification {request.validated['qualification']['_id']}",
                            extra=context_unpack(request, {"MESSAGE_ID": "qualification_patch"})
                        )
                else:
                    qualification_id = request.validated['qualification']['_id']
                    if save_object(request, "qualification", insert=True, raise_error_handler=True):
                        logger.info(
                            f"Created qualification {qualification_id}",
                            extra=context_unpack(
                                request,
                                {"MESSAGE_ID": "qualification_create"},
                                {"qualification_id": qualification_id},
                            )
                        )

            # save submission
            if save_object(request, "submission", raise_error_handler=True):
                logger.info(
                    f"Updated submission {request.validated['submission']['_id']} status",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "submission_patch"}),
                )


class BaseDocumentResource(FrameworkBaseResource, DocumentResourceMixin):
    state_class = BaseFrameworkDocumentState
    serializer_class = DocumentSerializer
    model_class = Document
    item_name = "framework"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        resolve_document(request, self.item_name, self.container)

    def save(self, **kwargs):
        return save_object(self.request, self.item_name, modified=self.get_modified(), **kwargs)

    def get_file(self):
        return get_file(self.request, item_name=self.item_name)
