'''
Created on Jan 2, 2011

@author: kyoncho
'''
import unittest

import main


class NavigatorTest(unittest.TestCase):

    def setUp(self):
        self.nav = main.Navigator()

    def tearDown(self):
        pass

    def testMoving(self):
        window1 = "window1"
        self.nav.putWindow(window1)

        window2 = "window2"
        self.nav.putWindow(window2)

        self.assertEqual(self.nav.moveForward(), None)
        self.assertEqual(self.nav.moveBackward(), window1)
        self.nav.putWindow(window1)
        self.assertEqual(self.nav.moveBackward(), window1)
        self.nav.putWindow(window1)
        self.assertEqual(self.nav.moveForward(), window2)
        self.nav.putWindow(window2)

 
    def testDeleteWindow(self):
        self.nav.putWindow("window1")
        self.nav.putWindow("window2")
        self.nav.putWindow("window3")

        self.nav.removeWindow("window2")
        self.assertEqual(self.nav.moveBackward(), "window1")

    def testDuplicateWindow(self):
        self.nav.putWindow("window1")
        self.nav.putWindow("window2")
        self.nav.putWindow("window1")

        self.assertEqual(self.nav.moveBackward(), "window2")
        self.nav.putWindow("window2")
        self.assertEqual(self.nav.moveBackward(), "window2")

    def testAddNone(self):
        self.nav.putWindow(None)
        self.nav.putWindow("window1")
        self.assertEqual(self.nav.moveBackward(), "window1")

    def testMoveForward(self):
        self.nav.putWindow("window1")
        self.nav.putWindow("window2")
        self.nav.putWindow("window3")
        self.nav.putWindow("window4")

        self.nav.putWindow(self.nav.moveBackward())
        self.nav.putWindow(self.nav.moveBackward())
        self.nav.putWindow(self.nav.moveBackward())
        
        self.assertEqual(self.nav.moveForward(), "window2")
        self.nav.putWindow("window2")
        self.assertEqual(self.nav.moveForward(), "window3")
        self.nav.putWindow("window3")
        self.assertEqual(self.nav.moveForward(), "window4")


    def runTest(self):
        self.run()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testMoving']
    unittest.main()