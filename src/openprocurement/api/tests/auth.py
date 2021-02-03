# -*- coding: utf-8 -*-
import os
import unittest
from pyramid import testing
from openprocurement.api.auth import AuthenticationPolicy
from hashlib import sha512
from pyramid.compat import bytes_


class AuthTest(unittest.TestCase):

    def _makeOne(self, *args, **kwargs):
        auth_file_path = "{}/auth.ini".format(os.path.dirname(os.path.abspath(__file__)))
        return AuthenticationPolicy(auth_file_path, realm="SomeRealm")

    def _getTargetClass(self):
        from pyramid.authentication import BasicAuthAuthenticationPolicy as cls
        return cls

    def test_class_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import IAuthenticationPolicy
        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_unauthenticated_userid(self):
        import base64
        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Basic %s' % base64.b64encode(
            bytes_('chrisr:password')).decode('ascii')
        policy = self._makeOne(None)
        self.assertEqual(policy.unauthenticated_userid(request), 'chrisr')

    def test_unauthenticated_userid_no_credentials(self):
        request = testing.DummyRequest()
        policy = self._makeOne(None)
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_unauthenticated_bad_header(self):
        request = testing.DummyRequest()
        request.headers['Authorization'] = '...'
        policy = self._makeOne(None)
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_unauthenticated_userid_not_basic(self):
        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Complicated things'
        policy = self._makeOne(None)
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_unauthenticated_userid_corrupt_base64(self):
        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Basic chrisr:password'
        policy = self._makeOne(None)
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_authenticated_userid(self):
        import base64
        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Basic %s' % base64.b64encode(
            bytes_('chrisr:password')).decode('ascii')
        def check(username, password, request):
            return []
        policy = self._makeOne(check)
        self.assertEqual(policy.authenticated_userid(request), 'chrisr')

    def test_authenticated_userid_utf8(self):
        import base64
        request = testing.DummyRequest()
        inputs = (b'm\xc3\xb6rk\xc3\xb6:'
                  b'm\xc3\xb6rk\xc3\xb6password').decode('utf-8')
        request.headers['Authorization'] = 'Basic %s' % (
            base64.b64encode(inputs.encode('utf-8')).decode('latin-1'))
        def check(username, password, request):
            return []
        policy = self._makeOne(check)
        self.assertEqual(policy.authenticated_userid(request),
                         b'm\xc3\xb6rk\xc3\xb6'.decode('utf-8'))

    def test_authenticated_userid_latin1(self):
        import base64
        request = testing.DummyRequest()
        inputs = (b'm\xc3\xb6rk\xc3\xb6:'
                  b'm\xc3\xb6rk\xc3\xb6password').decode('utf-8')
        request.headers['Authorization'] = 'Basic %s' % (
            base64.b64encode(inputs.encode('latin-1')).decode('latin-1'))
        def check(username, password, request):
            return []
        policy = self._makeOne(check)
        self.assertEqual(policy.authenticated_userid(request),
                         b'm\xc3\xb6rk\xc3\xb6'.decode('utf-8'))

    def test_unauthenticated_userid_invalid_payload(self):
        import base64
        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Basic %s' % base64.b64encode(
            bytes_('chrisrpassword')).decode('ascii')
        policy = self._makeOne(None)
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_remember(self):
        policy = self._makeOne(None)
        self.assertEqual(policy.remember(None, None), [])

    def test_forget(self):
        policy = self._makeOne(None)
        self.assertEqual(policy.forget(None), [
            ('WWW-Authenticate', 'Basic realm="SomeRealm"')])

    def test_unauthenticated_userid_bearer(self):
        request = testing.DummyRequest()
        request.headers["Authorization"] = "Bearer chrisr"
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), "chrisr")

    def test_principals_acc_token_param(self):
        request = testing.DummyRequest()
        request.params["acc_token"] = "token"
        self.assertPrincipals(request, "token")

    def test_principals_acc_token_param_utf8(self):
        request = testing.DummyRequest()
        request.params["acc_token"] = b'm\xc3\xb6rk\xc3\xb6'.decode("utf8")
        self.assertPrincipals(request, b'm\xc3\xb6rk\xc3\xb6'.decode("utf8"))

    def test_principals_acc_token_header(self):
        request = testing.DummyRequest()
        request.headers["X-Access-Token"] = "token"
        self.assertPrincipals(request, "token")

    def test_principals_acc_token_header_utf8(self):
        request = testing.DummyRequest()
        request.headers["X-Access-Token"] = b'm\xc3\xb6rk\xc3\xb6'.decode("utf8")
        self.assertPrincipals(request, b'm\xc3\xb6rk\xc3\xb6'.decode("utf8"))

    def test_principals_acc_token_body(self):
        request = testing.DummyRequest()
        request.content_type = "application/json"
        request.method = "POST"
        request.json = {'access': {"token": "token"}}
        self.assertPrincipals(request, "token")

    def test_principals_acc_token_body_utf8(self):
        request = testing.DummyRequest()
        request.content_type = "application/json"
        request.method = "POST"
        request.json = {'access': {"token": b'm\xc3\xb6rk\xc3\xb6'.decode("utf8")}}
        self.assertPrincipals(request, b'm\xc3\xb6rk\xc3\xb6'.decode("utf8"))

    def assertPrincipals(self, request, acc_token):
        policy = self._makeOne(None)
        principals = policy.principals("chrisr", request)
        self.assertIn("g:tests", principals)
        self.assertIn("a:1", principals)
        self.assertIn("a:2", principals)
        self.assertIn("a:3", principals)
        self.assertIn("a:4", principals)
        self.assertIn("chrisr_{}".format(acc_token), principals)
        self.assertIn("chrisr_{}".format(sha512(acc_token.encode("utf-8")).hexdigest()), principals)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
