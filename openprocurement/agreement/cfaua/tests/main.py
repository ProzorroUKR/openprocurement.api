import unittest
from openprocurement.agreement.cfaua.tests import (
    create, get)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(create.suite())
    suite.addTest(get.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')