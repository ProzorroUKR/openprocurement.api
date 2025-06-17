import unittest

from openprocurement.contracting.core.tests import document


def suite():
    suite = unittest.TestSuite()
    suite.addTest(document.suite())
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
