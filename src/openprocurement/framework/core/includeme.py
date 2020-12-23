# -*- coding: utf-8 -*-
from logging import getLogger

from pkg_resources import iter_entry_points

from openprocurement.framework.core.utils import (
    extract_doc,
    register_framework_frameworkType,
    register_submission_submissionType,
    register_qualification_qualificationType,
    isFramework,
    isSubmission,
    isQualification,
    framework_from_data,
    submission_from_data,
    qualification_from_data,
)

LOGGER = getLogger("openprocurement.framework.core")


def includeme(config):
    from openprocurement.framework.core.design import add_design
    LOGGER.info("Init framework.core plugin")

    add_design()
    config.add_request_method(extract_doc, "framework", reify=True)
    config.add_request_method(extract_doc, "submission", reify=True)
    config.add_request_method(extract_doc, "qualification", reify=True)

    # framework frameworkType plugins support
    config.registry.framework_frameworkTypes = {}
    config.registry.submission_submissionTypes = {}
    config.registry.qualification_qualificationTypes = {}
    config.add_route_predicate("frameworkType", isFramework)
    config.add_route_predicate("submissionType", isSubmission)
    config.add_route_predicate("qualificationType", isQualification)
    config.add_request_method(framework_from_data)
    config.add_request_method(submission_from_data)
    config.add_request_method(qualification_from_data)
    config.add_directive("add_framework_frameworkTypes", register_framework_frameworkType)
    config.add_directive("add_submission_submissionTypes", register_submission_submissionType)
    config.add_directive("add_qualification_qualificationTypes", register_qualification_qualificationType)
    config.scan("openprocurement.framework.core.views")

    # search for plugins
    settings = config.get_settings()
    plugins = settings.get("plugins") and [plugin.strip() for plugin in settings["plugins"].split(",")]
    for entry_point in iter_entry_points("openprocurement.framework.core.plugins"):
        if not plugins or entry_point.name in plugins:
            plugin = entry_point.load()
            plugin(config)
