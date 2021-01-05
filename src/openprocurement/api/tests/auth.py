# -*- coding: utf-8 -*-
import os
import unittest
from pyramid import testing
from openprocurement.api.auth import AuthenticationPolicy
from pyramid.tests.test_authentication import TestBasicAuthAuthenticationPolicy
from hashlib import sha512


class AuthTest(TestBasicAuthAuthenticationPolicy):
    def _makeOne(self, *args, **kwargs):
        auth_file_path = "{}/auth.ini".format(os.path.dirname(os.path.abspath(__file__)))
        return AuthenticationPolicy(auth_file_path, realm="SomeRealm")

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
        self.assertIn(u"g:tests", principals)
        self.assertIn(u"a:1", principals)
        self.assertIn(u"a:2", principals)
        self.assertIn(u"a:3", principals)
        self.assertIn(u"a:4", principals)
        self.assertIn(u"chrisr_{}".format(acc_token), principals)
        self.assertIn(u"chrisr_{}".format(sha512(acc_token.encode("utf-8")).hexdigest()), principals)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
