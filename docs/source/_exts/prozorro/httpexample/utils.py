import os
from importlib import resources


def resolve_path(spec, cwd=""):
    if os.path.isfile(os.path.normpath(os.path.join(cwd, spec))):
        return os.path.normpath(os.path.join(cwd, spec))
    elif spec.count(":"):
        package, path = spec.split(":", 1)
        try:
            resource = resources.files(package).joinpath(path)
        except (ModuleNotFoundError, TypeError):
            return spec
        if resource.is_file() or resource.is_dir():
            return str(resource)
    return spec
