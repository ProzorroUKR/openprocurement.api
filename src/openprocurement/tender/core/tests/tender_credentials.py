import unittest
from mock import MagicMock, patch
from hashlib import sha512

from openprocurement.tender.core.procedure.views.tender_credentials import TenderResource


class TestTenderCredentials(unittest.TestCase):
    def test_tender_credentials(self):
        request = MagicMock()
        context = MagicMock()
        tender = {"_id": "tender_id", "owner": "owner", "owner_token": "owner_token"}
        request.validated = {"tender": tender}
        response = TenderResource(request, context).get()

        self.assertEqual(sha512(tender["owner_token"].encode("utf-8")).hexdigest(), response["data"]["tender_token"])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTenderCredentials))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
