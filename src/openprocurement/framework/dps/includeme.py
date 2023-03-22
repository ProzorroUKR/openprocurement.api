# -*- coding: utf-8 -*-
from logging import getLogger

from openprocurement.framework.dps.models import (
    Framework,
    Submission,
    Qualification,
    Agreement,
)

LOGGER = getLogger("openprocurement.framework.dps")


def includeme(config):
    LOGGER.info("Init framework.dps plugin.")
    config.add_framework_frameworkTypes(Framework)
    config.add_submission_submissionTypes(Submission)
    config.add_qualification_qualificationTypes(Qualification)
    config.add_agreement_agreementTypes(Agreement)
    config.scan("openprocurement.framework.dps.views")
