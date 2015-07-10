'''
Created on Jan 1, 2011

@author: kyoncho
'''

import common
import gtk
import gtk.gdk
import main
import pygtk
import wnck

WORKSPACE_ITEM_WIDTH = 50
WORKSPACE_ITEM_HEIGHT = 20

logger = common.getLogger("Window")

class Window(gtk.Window):

    def __init__(self):
        logger.debug("__init__")

        super(gtk.Window, self).__init__()
        self.set_decorated(False)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_keep_above(True)
        self.connect("key-press-event", self._key_press_event)
        self.connect("focus-out-event", self._focus_changed)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self._table = gtk.Table()
        self.add(self._table)
        self.show_all()

    def setWorkspaces(self, workspaces):
        logger.debug("setWorkspaces")

        for child in self._table.get_children():
            self._table.remove(child)

        col = 0
        for ws in workspaces:
            row = 1
            header = self._createHeader(ws)
            self._table.attach(header, col, col + 1, 0, 1)
            for win in ws.windows:
                control = self._createWinControl(win)
                self._table.attach(control, col, col + 1, row, row + 1)
                row = row + 1
            col = col + 1

        self.show_all()

    def _key_press_event(self, sender, eventData):
        logger.debug("_key_press_event")
        if eventData.keyval == gtk.keysyms.Escape:
            self.hide()

    def _init(self, sender, eventData):
        print eventData.type

    def _focus_changed(self, sender, data):
        self.hide()

    def _createWinControl(self, win):
        pixmap = gtk.Image()
        pixmap.set_from_pixbuf(win.icon)
        hbox = gtk.HBox()
        label = gtk.Label(win.name[:20])
        label.set_tooltip_text(win.name)
        eventBox = gtk.EventBox()
        '''     eventBox.modify_bg(gtk.STATE_NORMAL,
                            eventBox.get_colormap().alloc_color("green"))'''
        eventBox.add(label)
        hbox.pack_start(pixmap, False, False)
        hbox.pack_start(eventBox, True, True)
        return hbox
    
    def _createHeader(self, workspace):
        label  = gtk.Label();
        label.set_text("Workspace: " + workspace.name)
        return label

class WindowData:
    control = None