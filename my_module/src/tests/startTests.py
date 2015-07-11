'''
Created on Jan 2, 2011

@author: kyoncho
'''

import tests.navigator
import unittest

if __name__ == '__main__':
    tl = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(tl.loadTestsFromModule(tests.navigator))
    unittest.TextTestRunner(verbosity=2).run(suite)

