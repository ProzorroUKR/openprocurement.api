# -*- coding: utf-8 -*-
from logging import getLogger

from openprocurement.framework.electroniccatalogue.models import (
    ElectronicCatalogueFramework,
    Submission,
    Qualification,
)

LOGGER = getLogger("openprocurement.framework.electroniccatalogue")


def includeme(config):
    LOGGER.info("Init framework.electroniccatalogue plugin.")
    config.add_framework_frameworkTypes(ElectronicCatalogueFramework)
    config.add_submission_submissionTypes(Submission)
    config.add_qualification_qualificationTypes(Qualification)
    config.scan("openprocurement.framework.electroniccatalogue.views")
