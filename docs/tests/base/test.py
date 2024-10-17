import io
import json
import mimetypes
import re
import traceback
from collections import defaultdict
from datetime import timedelta
from hashlib import md5
from unittest import mock
from uuid import UUID

from bson import Timestamp
from freezegun import freeze_time
from tests.base.constants import API_HOST, MOCK_DATETIME, PUBLIC_API_HOST
from webtest import forms
from webtest.compat import to_bytes

from openprocurement.api.tests.base import BaseTestApp
from openprocurement.api.utils import get_now


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
        resp = super().do_request(req, status=status, expect_errors=expect_errors)
        self.write_response(resp)
        return resp

    def write_request(self, req):
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            host = req.host_url
            url = req.url[len(host) :]
            parts = ['{} {} {}'.format(req.method, url, req.http_version)]

            headerlist = self.filter_headerlist(req.headers.items())
            for k, v in sorted(headerlist):
                header = '{}: {}'.format(k, v)
                parts.append(header)

            parts.append('')

            if req.body:
                try:
                    obj = json.loads(req.body)
                except ValueError:
                    parts.append(req.body.decode('utf8'))
                else:
                    parts.append(json.dumps(obj, indent=self.indent, ensure_ascii=self.ensure_ascii))

                parts.append('')

            parts.append('')

            text = '\n'.join(parts)

            if isinstance(self.file_obj, io.TextIOWrapper):
                self.file_obj.write(text)
            else:
                self.file_obj.write(text.encode('utf8'))

    def write_response(self, resp):
        if hasattr(self, 'file_obj') and not self.file_obj.closed:

            parts = ['', '{} {}'.format(resp.request.http_version, resp.status)]

            headerlist = self.filter_headerlist(resp.headerlist)
            for k, v in sorted(headerlist):
                header = '{}: {}'.format(k, v)
                parts.append(header)

            parts.append('')

            if resp.testbody:
                try:
                    obj = json.loads(resp.testbody)
                except ValueError:
                    pass
                else:
                    parts.append(json.dumps(obj, indent=self.indent, ensure_ascii=self.ensure_ascii))

                    parts.append('')

            parts.append('')

            text = '\n'.join(parts)

            if isinstance(self.file_obj, io.TextIOWrapper):
                self.file_obj.write(text)
            else:
                self.file_obj.write(text.encode('utf8'))

    @staticmethod
    def filter_headerlist(headerlist):
        exclude_headers = (
            'content-length',
            'set-cookie',
        )
        exclude_prefixes = ('x-',)
        filtered_headerlist = []
        for k, v in headerlist:
            if k.lower() in exclude_headers:
                continue
            if any(k.lower().startswith(prefix) for prefix in exclude_prefixes):
                continue
            filtered_headerlist.append((k, v))
        return filtered_headerlist

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
            if isinstance(key, str):
                try:
                    key = key.encode('ascii')
                except:  # pragma: no cover
                    raise  # file name must be ascii
            if isinstance(filename, str):
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
                    b'Content-Disposition: form-data; ' + b'name="' + key + b'"; filename="' + filename + b'"',
                    b'Content-Type: ' + fcontent,
                    b'',
                    value,
                ]
            )

        for key, value in params:
            if isinstance(key, str):
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
                if isinstance(value, str):
                    value = value.encode('utf8')
                lines.extend([b'--' + boundary, b'Content-Disposition: form-data; name="' + key + b'"', b'', value])

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
            invalid_value = "You should use a value like ('Basic', ('user', 'password'))"
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


class MockWebTestMixin:
    uuid_patch = None
    uuid_counters = None
    freezer = None
    tick_delta = None

    freezing_datetime = MOCK_DATETIME

    whitelist = ('/openprocurement/', '/openprocurement/.*/tests/', 'docs/tests')
    blacklist = (r'/tests/base/test\.py',)

    def setUpMock(self):
        self.uuid_patch = mock.patch('uuid.UUID', side_effect=self.uuid)
        self.uuid_patch.start()
        self.db_now_path = mock.patch('openprocurement.api.database.get_public_modified', lambda: get_now().timestamp())
        self.db_now_path.start()

        # https://www.mongodb.com/docs/v4.4/reference/bson-types/#timestamps
        increments = defaultdict(int)

        def get_mocked_bson_timestamp():
            seconds = int(get_now().timestamp())
            key = str(seconds)
            increments[key] += 1
            return Timestamp(seconds, increments[key])

        self.db_timestamp_path = mock.patch('openprocurement.api.database.get_public_ts', get_mocked_bson_timestamp)
        self.db_timestamp_path.start()

        self.freezer = freeze_time(self.freezing_datetime)
        self.freezer.start()

    def tearDownMock(self):
        self.freezer.stop()
        self.uuid_patch.stop()
        self.db_now_path.stop()
        self.db_timestamp_path.stop()
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
                    return path[found.span()[0] :]

        stack = traceback.extract_stack()
        return [
            (trim_path(item[0]), item[2], item[3])
            for item in stack
            if all(
                [
                    any([re.search(pattern, item[0]) is not None for pattern in self.whitelist]),
                    all([re.search(pattern, item[0]) is None for pattern in self.blacklist]),
                ]
            )
        ]

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
