# -*- coding: utf-8 -*-
import os
import pkg_resources


def resolve_path(spec, cwd=''):
    if os.path.isfile(os.path.normpath(os.path.join(cwd, spec))):
        return os.path.normpath(os.path.join(cwd, spec))
    elif (spec.count(':') and
          pkg_resources.resource_exists(*spec.split(':', 1))):
        return pkg_resources.resource_filename(*spec.split(':', 1))
    else:
        return spec
