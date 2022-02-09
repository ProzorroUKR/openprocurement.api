# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.belowthreshold.tests.document import TenderDocumentWithDSResourceTestMixin

from openprocurement.tender.cfaua.tests.base import BaseTenderContentWebTest


class TenderDocumentWithDSResourceTest(BaseTenderContentWebTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True
    initial_auth = ("Basic", ("broker", ""))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
