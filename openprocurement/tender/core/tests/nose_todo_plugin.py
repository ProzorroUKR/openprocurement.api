"""This plugin installs a TODO warning class for the Warning exception.
When Warning is raised, the exception will be logged in the todo
attribute of the result, 'W' or 'WarnTODO' (verbose) will be output, and
the exception will not be counted as an error or failure. This plugin
is disabled by default but may be enabled with the ``--with-todo`` option.
"""
from nose.plugins.errorclass import ErrorClass, ErrorClassPlugin
from functools import wraps


class TodoWarningPlugin(ErrorClassPlugin):
    """ Installs a TODO warning class for the Warning exception.

    When Warning is raised, the exception will be logged
    in the todo attribute of the result, 'W' or 'WarnTODO' (verbose)
    will be output, and the exception will not be counted as an error
    or failure.
    """
    name = 'todo'
    todo = ErrorClass(Warning, label='WarnTODO', isfailure=False)


def warnTODO(reason):
    """ Decorator for skipping test by raising Warning with reason.
    """
    def decorator(test_item):
        @wraps(test_item)
        def warn_wrapper(*args, **kwargs):
            raise Warning('this test requires: {}'.format(reason))
        test_item = warn_wrapper
        test_item.todo = reason
        return test_item
    return decorator
