# -*- coding: utf-8 -*-
import binascii
from hashlib import sha512
from pyramid.authentication import BasicAuthAuthenticationPolicy, b64decode
from configparser import ConfigParser
from pyramid.interfaces import IAuthenticationPolicy

ACCR_1 = '1'
ACCR_2 = '2'
ACCR_3 = '3'
ACCR_4 = '4'
ACCR_5 = '5'
ACCR_COMPETITIVE = 'c'
ACCR_EXIT = 'x'
ACCR_TEST = 't'

DEFAULT_ACCRS = ''.join([ACCR_1, ACCR_2, ACCR_3, ACCR_4, ACCR_5])


class AuthenticationPolicy(BasicAuthAuthenticationPolicy):
    """
    Authentication policy which uses HTTP standard bearer and basic
    authentication protocol to authenticate users. To use this policy you will
    need to provide configuration file with auth users data.

    Constructor Arguments

    ``auth_file``

        A configuration file consists of sections, each led by a [section] header,
        followed by key/value entries separated by a specific string (=).  Section
        is responsible for auth group.  Each key/value in section are user
        credentials.  Key as username and value as auth key or key/accreditation
        separated by a specific string (,).  In case of accreditation level is not
        provided (no separator in value) default accreditation is "1234".

        Example::

        ```
        [brokers]
        chrisr = chrisr,1234
        smithumble = smithumble,

        [admins]
        mörkö = mörkö
        ```

    ``realm``

        Default: ``"OpenProcurement"``.  The Basic Auth Realm string.  Usually displayed to
        the user by the browser in the login dialog.

    ``debug``

        Default: ``False``.  If ``debug`` is ``True``, log messages to the
        Pyramid debug logger about the results of various authentication
        steps.  The output from debugging is useful for reporting to maillist
        or IRC channels when asking for support.
    """
    def __init__(self, auth_file, realm="OpenProcurement", debug=False):
        super(AuthenticationPolicy, self).__init__(None, realm=realm, debug=debug)
        self.users = read_auth_users(auth_file, encoding="utf8", default_level=DEFAULT_ACCRS)

    def unauthenticated_userid(self, request):
        """
        The userid parsed from the ``Authorization`` request header.
        """
        return self.users.get(extract_http_credentials(request), {}).get("name")

    def callback(self, username, request):
        # Username arg is ignored. Unfortunately extract_http_credentials winds up
        # getting called twice when authenticated_userid is called.  Avoiding
        # that, however, winds up duplicating logic from the superclass.
        return self.principals(extract_http_credentials(request), request)

    def principals(self, key, request):
        """
        Returns ``None`` if the user doesn't exist or a sequence
        of principal identifiers (possibly empty) if the user does exist.
        """
        user =  self.users.get(key)
        if user:
            principals = ["g:%s" % user["group"]]
            for i in user["level"]:
                principals.append("a:%s" % i)
            acc_token = extract_access_token(request)
            if acc_token:
                acc_token_hex = sha512(acc_token.encode("utf-8")).hexdigest()
                principals.append("%s_%s" % (user["name"], acc_token))
                principals.append("%s_%s" % (user["name"], acc_token_hex))
            return principals


def get_local_roles(context):
    from pyramid.location import lineage

    roles = {}
    for location in reversed(list(lineage(context))):
        try:
            local_roles = location.__local_roles__
        except AttributeError:
            continue
        if local_roles and callable(local_roles):
            local_roles = local_roles()
        roles.update(local_roles)
    return roles


def authenticated_role(request):
    principals = request.effective_principals
    if hasattr(request, "context"):
        roles = get_local_roles(request.context)
        local_roles = [roles[i] for i in reversed(principals) if i in roles]
        if local_roles:
            return local_roles[0]
    groups = [g for g in reversed(principals) if g.startswith("g:")]
    return groups[0][2:] if groups else "anonymous"


def check_accreditation(request, level):
    return "a:{}".format(level) in request.effective_principals


def check_accreditations(request, levels):
    return any([check_accreditation(request, level) for level in levels])


def check_user_accreditation(request, userid, level, default=False):
    policy = request.registry.queryUtility(IAuthenticationPolicy)
    for user in policy.users.values():
        if user["name"] == userid:
            return level in user["level"]
    return default


def check_user_accreditations(request, userid, levels, default=False):
    return any([check_user_accreditation(request, userid, level, default=default) for level in levels])


def extract_http_credentials(request):
    """
    A helper function for extraction of HTTP credentials
    from a given request.
    Returns a auth token or ``None`` if no credentials could be found.
    """
    authorization = request.headers.get('Authorization')
    if not authorization:
        return None

    try:
        authmeth, auth = authorization.split(' ', 1)
    except ValueError:  # not enough values to unpack
        return None

    if authmeth.lower() == 'bearer':
        return auth

    if authmeth.lower() != 'basic':
        return None

    try:
        authbytes = b64decode(auth.strip())
    except (TypeError, binascii.Error): # can't decode
        return None

    # try utf-8 first, then latin-1; see discussion in
    # https://github.com/Pylons/pyramid/issues/898
    try:
        auth = authbytes.decode('utf-8')
    except UnicodeDecodeError:
        auth = authbytes.decode('latin-1')

    try:
        return auth.split(':', 1)[0]
    except ValueError: # not enough values to unpack
        return None



def extract_access_token(request):
    token = request.params.get("acc_token") or request.headers.get("X-Access-Token")
    if not token and request.method in ["POST", "PUT", "PATCH"] and request.content_type == "application/json":
        try:
            json = request.json_body
        except ValueError:
            json = None
        token = json.get("access", {}).get("token") if isinstance(json, dict) else None
    return token


def read_auth_users(auth_file, encoding="utf8", default_level=""):
    config = ConfigParser()
    config.read(auth_file, encoding=encoding)
    users = {}
    for i in config.sections():
        for j, k in config.items(i):
            info = k.split(",", 1)
            key = info[0]
            level = info[1] if "," in k else default_level
            user = {"name": j, "level": level, "group": i}
            users.update({key: user})
    return users
