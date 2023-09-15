# -*- coding: utf-8 -*-
from logging import getLogger

from openprocurement.framework.electroniccatalogue.procedure.models.submission import Submission
from openprocurement.framework.electroniccatalogue.procedure.models.agreement import Agreement
from openprocurement.framework.electroniccatalogue.procedure.models.framework import Framework
from openprocurement.framework.electroniccatalogue.procedure.models.qualification import Qualification

LOGGER = getLogger("openprocurement.framework.electroniccatalogue")


def includeme(config):
    LOGGER.info("Init framework.electroniccatalogue plugin.")
    config.add_framework_frameworkTypes(Framework)
    config.add_submission_submissionTypes(Submission)
    config.add_qualification_qualificationTypes(Qualification)
    config.add_agreement_agreementTypes(Agreement)
    # config.scan("openprocurement.framework.electroniccatalogue.views")
    config.scan("openprocurement.framework.electroniccatalogue.procedure.views")
