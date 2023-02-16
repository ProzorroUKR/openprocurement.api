from openprocurement.api.context import set_db_session
from logging import getLogger
from bson.json_util import dumps, loads
from base64 import b64encode, b64decode

LOGGER = getLogger(__name__)


class DBSessionCookieMiddleware:
    cookie_name = "SESSION"
    """ 
    Passes cluster_time & operation_time between requests of a client
    to provide casual consistency 
    """
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        warning = None

        with self.registry.mongodb.connection.start_session(causal_consistency=True) as session:
            cookie = request.cookies.get(self.cookie_name)
            if cookie:
                try:
                    values = loads(b64decode(cookie))
                    session.advance_cluster_time(values["cluster_time"])
                    session.advance_operation_time(values["operation_time"])
                except Exception as exc:
                    warning = f"Error on {self.cookie_name} cookie parsing: {exc}"
                    LOGGER.debug(warning)

            set_db_session(session)
            try:
                response = self.handler(request)  # processing request
            finally:
                set_db_session(None)

        if warning:
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Warning
            response.headers["Warning"] = f"199 - \"{warning}\""

        session_data = {
            "operation_time": session.operation_time,
            "cluster_time": session.cluster_time,
        }
        response.set_cookie(
            name=self.cookie_name,
            value=b64encode(dumps(session_data).encode()),
        )
        return response
