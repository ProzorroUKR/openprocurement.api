import json
import traceback
import io
import mimetypes
import re

from datetime import timedelta

import mock
from freezegun import freeze_time
from openprocurement.api.tests.base import BaseTestApp
from openprocurement.api.utils import get_now
from uuid import UUID
from hashlib import md5
from six import text_type
from webtest.compat import to_bytes
from webtest import forms

from tests.base.constants import (
    API_HOST,
    MOCK_DATETIME,
    PUBLIC_API_HOST,
)


class DumpsWebTestApp(BaseTestApp):
    hostname = API_HOST
    public_hostname = PUBLIC_API_HOST
    indent = 2
    ensure_ascii = False

    def do_request(self, req, status=None, expect_errors=None):
        if req.method == "GET":
            req.headers.environ["HTTP_HOST"] = self.public_hostname
        else:
            req.headers.environ["HTTP_HOST"] = self.hostname
        self.write_request(req)
        resp = super(DumpsWebTestApp, self).do_request(req, status=status, expect_errors=expect_errors)
        self.write_response(resp)
        return resp

    def write_request(self, req):
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            if isinstance(self.file_obj, io.TextIOWrapper):
                self.file_obj.write(req.as_bytes(True).decode("utf-8"))
                self.file_obj.write("\n")
                if req.body:
                    try:
                        obj = json.loads(req.body)
                    except ValueError:
                        self.file_obj.write('\n' + req.body.decode("utf-8"))
                    else:
                        self.file_obj.write(
                            '\n' + json.dumps(
                                obj, indent=self.indent, ensure_ascii=self.ensure_ascii
                            )
                            )
                    self.file_obj.write("\n")
                self.file_obj.write("\n")
            else:
                self.file_obj.write(req.as_bytes(True))
                self.file_obj.write(b"\n")
                if req.body:
                    try:
                        obj = json.loads(req.body)
                    except ValueError:
                        self.file_obj.write(b'\n' + req.body)
                    else:
                        self.file_obj.write(
                            b'\n' + json.dumps(
                                obj, indent=self.indent, ensure_ascii=self.ensure_ascii
                            ).encode('utf8')
                            )
                    self.file_obj.write(b"\n")
                self.file_obj.write(b"\n")

    def write_response(self, resp):
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            exclude_headers = ('content-length', 'set-cookie')
            exclude_prefixes = ('x-',)
            headers = [
                (n.title(), v)
                for n, v in resp.headerlist
                if n.lower() not in exclude_headers and not n.lower().startswith(exclude_prefixes)
            ]
            headers.sort()
            header = str('\nHTTP/1.0 %s\n%s\n') % (
                resp.status,
                str('\n').join([str('%s: %s') % (n, v) for n, v in headers]),
            )
            body = None
            if resp.testbody:
                try:
                    obj = json.loads(resp.testbody)
                except ValueError:
                    pass
                else:
                    body = json.dumps(
                        obj, indent=self.indent, ensure_ascii=self.ensure_ascii
                    )
            if isinstance(self.file_obj, io.TextIOWrapper):
                self.file_obj.write(header)
                self.file_obj.write("\n")
                if body:
                    self.file_obj.write(body)
                    self.file_obj.write("\n")
                self.file_obj.write("\n")
            else:
                self.file_obj.write(header.encode('utf8'))
                self.file_obj.write(b"\n")
                if body:
                    self.file_obj.write(body.encode('utf8'))
                    self.file_obj.write(b"\n")
                self.file_obj.write(b"\n")

    def encode_multipart(self, params, files):
        """
        Encodes a set of parameters (typically a name/value list) and
        a set of files (a list of (name, filename, file_body, mimetype)) into a
        typical POST body, returning the (content_type, body).

        """
        boundary = b'---BOUNDARY'
        lines = []

        def _append_file(file_info):
            key, filename, value, fcontent = self._get_file_info(file_info)
            if isinstance(key, text_type):
                try:
                    key = key.encode('ascii')
                except:  # pragma: no cover
                    raise  # file name must be ascii
            if isinstance(filename, text_type):
                try:
                    filename = filename.encode('utf8')
                except:  # pragma: no cover
                    raise  # file name must be ascii or utf8
            if not fcontent:
                fcontent = mimetypes.guess_type(filename.decode('utf8'))[0]
            fcontent = to_bytes(fcontent)
            fcontent = fcontent or b'application/octet-stream'
            lines.extend(
                [
                    b'--' + boundary,
                    b'Content-Disposition: form-data; ' +
                    b'name="' + key + b'"; filename="' + filename + b'"',
                    b'Content-Type: ' + fcontent, b'', value]
            )

        for key, value in params:
            if isinstance(key, text_type):
                try:
                    key = key.encode('ascii')
                except:  # pragma: no cover
                    raise  # field name are always ascii
            if isinstance(value, forms.File):
                if value.value:
                    _append_file([key] + list(value.value))
            elif isinstance(value, forms.Upload):
                file_info = [key, value.filename]
                if value.content is not None:
                    file_info.append(value.content)
                    if value.content_type is not None:
                        file_info.append(value.content_type)
                _append_file(file_info)
            else:
                if isinstance(value, text_type):
                    value = value.encode('utf8')
                lines.extend(
                    [
                        b'--' + boundary,
                        b'Content-Disposition: form-data; name="' + key + b'"',
                        b'', value]
                )

        for file_info in files:
            _append_file(file_info)

        lines.extend([b'--' + boundary + b'--', b''])
        body = b'\r\n'.join(lines)
        boundary = boundary.decode('ascii')
        content_type = 'multipart/form-data; boundary=%s' % boundary
        return content_type, body

    def get_authorization(self):
        """Allow to set the HTTP_AUTHORIZATION environ key. Value should looks
        like ``('Basic', ('user', 'password'))``

        If value is None the the HTTP_AUTHORIZATION is removed
        """
        return self.authorization_value

    def set_authorization(self, value):
        self.authorization_value = value
        if value is not None:
            invalid_value = (
                "You should use a value like ('Basic', ('user', 'password'))"
            )
            if isinstance(value, (list, tuple)) and len(value) == 2:
                authtype, val = value
                if authtype == 'Basic' and val and isinstance(val, (list, tuple)):
                    key = val[0]
                else:
                    raise ValueError(invalid_value)
                value = str('Bearer %s' % key)
            else:
                raise ValueError(invalid_value)
            self.extra_environ.update(
                {
                    'HTTP_AUTHORIZATION': value,
                }
            )
        else:
            if 'HTTP_AUTHORIZATION' in self.extra_environ:
                del self.extra_environ['HTTP_AUTHORIZATION']

    authorization = property(get_authorization, set_authorization)


class MockWebTestMixin(object):
    uuid_patch = None
    uuid_counters = None
    freezer = None
    tick_delta = None

    whitelist = ('/openprocurement/', '/openprocurement/.*/tests/', 'docs/tests')
    blacklist = ('/tests/base/test\.py',)

    def setUpMock(self):
        self.uuid_patch = mock.patch('uuid.UUID', side_effect=self.uuid)
        self.uuid_patch.start()
        self.db_now_path = mock.patch(
            'openprocurement.api.database.get_public_modified',
            lambda: get_now().timestamp()
        )
        self.db_now_path.start()
        self.freezer = freeze_time(MOCK_DATETIME)
        self.freezer.start()

    def tearDownMock(self):
        self.freezer.stop()
        self.uuid_patch.stop()
        self.db_now_path.stop()
        self.uuid_counters = None

    def uuid(self, version=None, **kwargs):
        stack = self.stack()
        hex = md5(str(stack).encode("utf-8")).hexdigest()
        count = self.count(hex)
        hash = md5((hex + str(count)).encode("utf-8")).digest()
        return UUID(bytes=hash[:16], version=version)

    def stack(self):
        def trim_path(path):
            for whitelist_item in self.whitelist:
                found = re.search(whitelist_item, path)
                if found:
                    return path[found.span()[0]:]

        stack = traceback.extract_stack()
        return [(trim_path(item[0]), item[2], item[3]) for item in stack if all(
            [
                any([re.search(pattern, item[0]) is not None for pattern in self.whitelist]),
                all([re.search(pattern, item[0]) is None for pattern in self.blacklist])
            ]
        )]

    def count(self, name):
        if self.uuid_counters is None:
            self.uuid_counters = dict()
        if name not in self.uuid_counters:
            self.uuid_counters[name] = 0
        self.uuid_counters[name] += 1
        return self.uuid_counters[name]

    def tick(self, delta=timedelta(seconds=1)):
        if not self.tick_delta:
            self.tick_delta = timedelta(seconds=0)
        self.tick_delta += delta
        freeze = get_now() + self.tick_delta
        self.freezer.stop()
        self.freezer = freeze_time(freeze.isoformat())
        self.freezer.start()
