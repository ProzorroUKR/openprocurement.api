from logging import getLogger

from pkg_resources import iter_entry_points

from openprocurement.framework.core.database import (
    AgreementCollection,
    FrameworkCollection,
    QualificationCollection,
    SubmissionCollection,
)
from openprocurement.framework.core.procedure.serializers.agreement import (
    AgreementConfigSerializer,
)
from openprocurement.framework.core.procedure.serializers.framework import (
    FrameworkConfigSerializer,
)
from openprocurement.framework.core.procedure.serializers.qualification import (
    QualificationConfigSerializer,
)
from openprocurement.framework.core.procedure.serializers.submission import (
    SubmissionConfigSerializer,
)
from openprocurement.framework.core.procedure.utils import (
    extract_agreement_doc,
    extract_framework_doc,
    extract_qualification_doc,
    extract_submission_doc,
)
from openprocurement.framework.core.utils import (
    AgreementTypePredicate,
    FrameworkTypePredicate,
    QualificationTypePredicate,
    SubmissionTypePredicate,
)

LOGGER = getLogger("openprocurement.framework.core")


def includeme(config):
    LOGGER.info("Init framework.core plugin")

    config.registry.mongodb.add_collection("frameworks", FrameworkCollection)
    config.registry.mongodb.add_collection("agreements", AgreementCollection)
    config.registry.mongodb.add_collection("submissions", SubmissionCollection)
    config.registry.mongodb.add_collection("qualifications", QualificationCollection)

    config.add_request_method(extract_framework_doc, "framework_doc", reify=True)
    config.add_request_method(extract_submission_doc, "submission_doc", reify=True)
    config.add_request_method(extract_qualification_doc, "qualification_doc", reify=True)
    config.add_request_method(extract_agreement_doc, "agreement_doc", reify=True)

    config.add_route_predicate("frameworkType", FrameworkTypePredicate)
    config.add_route_predicate("submissionType", SubmissionTypePredicate)
    config.add_route_predicate("qualificationType", QualificationTypePredicate)
    config.add_route_predicate("agreementType", AgreementTypePredicate)

    config.add_config_serializer("framework", FrameworkConfigSerializer)
    config.add_config_serializer("submission", SubmissionConfigSerializer)
    config.add_config_serializer("qualification", QualificationConfigSerializer)
    config.add_config_serializer("agreement", AgreementConfigSerializer)

    config.scan("openprocurement.framework.core.procedure.views")

    # search for plugins
    settings = config.get_settings()
    plugins = settings.get("plugins") and [plugin.strip() for plugin in settings["plugins"].split(",")]
    for entry_point in iter_entry_points("openprocurement.framework.core.plugins"):
        if not plugins or entry_point.name in plugins:
            plugin = entry_point.load()
            plugin(config)
