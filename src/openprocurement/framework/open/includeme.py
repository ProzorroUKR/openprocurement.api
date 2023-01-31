# -*- coding: utf-8 -*-
from logging import getLogger

from openprocurement.framework.open.models import (
    Framework,
    Submission,
    Qualification,
    Agreement,
)

LOGGER = getLogger("openprocurement.framework.open")


def includeme(config):
    LOGGER.info("Init framework.open plugin.")
    config.add_framework_frameworkTypes(Framework)
    config.add_submission_submissionTypes(Submission)
    config.add_qualification_qualificationTypes(Qualification)
    config.add_agreement_agreementTypes(Agreement)
    config.scan("openprocurement.framework.open.views")
