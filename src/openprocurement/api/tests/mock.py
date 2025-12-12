from functools import wraps
from unittest.mock import patch


class ContextDecorator:
    """A base class that can be used as both a context manager and a decorator."""

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper

    def __enter__(self):
        """Enter the context. Subclasses must override this method."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context. Subclasses must override this method."""

    def start(self):
        """Start the context."""
        self.__enter__()
        return self

    def stop(self):
        """Exit the context."""
        self.__exit__(None, None, None)


class patch_multiple(ContextDecorator):
    """Patch multiple targets with the same mock object."""

    def __init__(self, targets, value):
        self.targets = targets
        self.value = value
        self.patchers = None

    def __enter__(self):
        self.patchers = [patch(target, self.value) for target in self.targets]
        for patcher in self.patchers:
            patcher.start()
        return self

    def __exit__(self, *exc_info):
        if self.patchers:
            for patcher in self.patchers:
                patcher.stop()
            self.patchers = None
