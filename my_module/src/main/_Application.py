'''
Created on Jan 1, 2011

@author: kyoncho
'''

import gtk


''' Application class containing logic for GTK start.
''' 
class _Application:
    '''
    classdocs
    '''

    def __init__(self, mainWindow):
        '''
        Constructor
        '''
        mainWindow.connect("destroy", self.__destroy)
        self._window = mainWindow

    def start(self):
        self._window.show()
        self._window.hide()
        gtk.main()

    def __destroy(self, args):
        print "Ending GTK loop"
        gtk.main_quit()