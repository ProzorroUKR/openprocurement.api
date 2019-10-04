# -*- coding: utf-8 -*-
from openprocurement.agreement.cfaua.traversal import factory
from functools import partial
from cornice.resource import resource as cornice_resource
from openprocurement.api.utils import error_handler
from cornice.resource import resource

agreements_resource = partial(cornice_resource, factory=factory, error_handler=error_handler)
