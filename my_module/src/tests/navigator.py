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
        self.assertEqual(self.nav.moveBackward(), None)
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
        self.assertEqual(self.nav.moveBackward(), None)

    def testAddNone(self):
        self.nav.putWindow(None)
        self.nav.putWindow("window1")
        self.assertIsNone(self.nav.moveBackward())

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


class TestColorParsing(unittest.TestCase):

    def testParsingColor(self):
        input = 'tooltip_fg_color: #212121212121\n' + \
                'link_color: #00008888cccc\n' + \
                'base_color: #f7f7f7f7f7f7\n' + \
                'selected_fg_color: #f5f5f5f5f5f5\n' + \
                'text_color: #212121212121\n' + \
                'bg_color: #d6d6d6d6d6d6\n' + \
                'tooltip_bg_color: #fbfbeaeaa0a 0\n' +  \
                'selected_bg_color: #9a9ab8b87c7c\n' + \
                'fg_color: #212121212121\n'

        self.assertEquals(main.getColor(input, "selected_bg_color"),
                          gtk.gdk.color_parse("#9a9ab8b87c7c"))


import gtk


class TestPressEventToString(unittest.TestCase):

    def testParsingColor(self):
        eventData = gtk.gdk.Event(gtk.gdk.KEY)


if __name__ == "__main__":
    unittest.main()
