'''
Created on Jan 1, 2011

@author: kyoncho
'''

import common
import gtk
import gtk.gdk

WORKSPACE_ITEM_WIDTH = 50
WORKSPACE_ITEM_HEIGHT = 20

logger = common.getLogger("Window")


# class Window(gtk.Window):
#     def __init__(self):
#         logger.debug("__init__")

#         super(gtk.Window, self).__init__()
#         self.set_decorated(False)
#         self.set_position(gtk.WIN_POS_CENTER)
#         self.set_keep_above(True)
#         self.connect("key-press-event", self._key_press_event)
#         self.connect("focus-out-event", self._focus_changed)
#         self.set_skip_pager_hint(True)
#         self.set_skip_taskbar_hint(True)
#         self._table = gtk.Table()
#         self.add(self._table)
#         self.show_all()
#         self.__eventBoxToWindow = {}

#     def setWorkspaces(self, workspaces):
#         logger.debug("setWorkspaces")
#         self.__eventBoxToWindow = {}

#         for child in self._table.get_children():
#             self._table.remove(child)

#         col = 0
#         windowIndex = 0
#         for ws in workspaces:
#             row = 1
#             header = self._createHeader(ws)
#             self._table.attach(header, col, col + 1, 0, 1)
#             for win in ws.windows:
#                 frame = gtk.Frame()
#                 windowIndex = windowIndex + 1
#                 control = self._createWinControl(win, windowIndex)
#                 frame.add(control)
#                 self._table.attach(frame, col, col + 1, row, row + 1)
#                 row = row + 1
#                 col = col + 1
#                 self.set_default_size(-1, -1)
#                 self.show_all()
#                 self.present()
#                 self.set_resizable(False)

#     def _key_press_event(self, sender, eventData):
#         logger.debug("_key_press_event")
#         if eventData.keyval == gtk.keysyms.Escape:
#             self.hide()

#     def _focus_changed(self, sender, data):
#         self.hide()

#     def _createWinControl(self, win, windowIndex):
#         hbox = gtk.HBox()
#         labelText = win.name.decode('utf-8')
#         labelText = "%s %s" % (windowIndex, labelText[:30])

#         if(win.isActive()):
#             label = gtk.Label("<b>" + labelText + "</b>")
#         else:
#             label = gtk.Label(labelText)

#         label.set_use_markup(True)
#         label.set_tooltip_text(win.name)
#         eventBox = gtk.EventBox()
#         self.__eventBoxToWindow[eventBox] = win

#         eventBox.add(label)
#         eventBox.connect("button-press-event", self._on_button_press_event)

#         pixmap = gtk.Image()
#         pixmap.set_from_pixbuf(win.icon)
#         hbox.pack_start(pixmap, False, False)

#         hbox.pack_start(eventBox, True, True)
#         return hbox

#     def _createHeader(self, workspace):
#         label = gtk.Label()
#         label.set_text("Workspace: " + workspace.name)
#         return label

#     def _on_button_press_event(self, sender, eventData):
#         win = self.__eventBoxToWindow[sender]
#         win.activate()
