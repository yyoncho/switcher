'''
Created on Jan 1, 2011

@author: kyoncho
'''
import time
import keybinder
import common
import wnck
import gtk

from _Application import _Application as App

logger = common.getLogger("default")

FORWARD_KEY = "<ctrl><alt>n"
BACKWARD_KEY = "<ctrl><alt>p"
WORKSPACE_ITEM_WIDTH = 50
WORKSPACE_ITEM_HEIGHT = 20


class Navigator:
    def __init__(self):
        self._back = list()
        self._forward = list()

    def moveForward(self):
        logger.debug("moveForward")
        if(not self._forward):
            return None
        result = self._forward[-1]
        self._printLocal()
        return result

    def moveBackward(self):
        logger.debug("moveBackward")
        ret = None
        if len(self._back) > 1:
            last = self._back.pop()
            self._forward.append(last)
            ret = self._back[-1]

        self._printLocal()
        return ret

    def putWindow(self, window):
        logger.debug("putWindow")

        if self._forward.count(window):
            self._forward.remove(window)

        if window:
            if self._back.count(window):
                self._back.remove(window)
            self._back.append(window)

        self._printLocal()

    def removeWindow(self, window):
        if self._back.count(window):
            self._back.remove(window)

        if self._forward.count(window):
            self._forward.remove(window)
        self._printLocal()

    def _printLocal(self):
        logger.debug("back=%s, forward=%s" %
                     (map(self.getWindowName, self._back),
                      map(self.getWindowName, self._forward)))

    def getWindowName(self, win):
        if hasattr(win, 'get_name'):
            return win.get_name().decode('utf8')
        else:
            return win


class Configuration:
    def getConfig(self, config):
        if(config == "forward"):
            return FORWARD_KEY
        else:
            return BACKWARD_KEY


class KeyboardManager:
    def __init__(self, nav, conf, screen, mainWindow):
        self.nav = nav
        self.configuration = conf
        screen.connect("active-window-changed",
                       self.window_focused_switch_handler)
        screen.connect("window-closed", self.window_deleted)

        forwKey = conf.getConfig("forward")
        success = keybinder.bind(forwKey, self.move_forward, None)
        if not success:
            raise Exception("Failed to register key " + forwKey)

        backKey = conf.getConfig("backward")
        success = keybinder.bind(backKey, self.move_backward, None)
        if not success:
            raise Exception("Failed to register key " + backKey)

        displayWindowKey = "<ctrl><alt>g"
        success = keybinder.bind(displayWindowKey, self._display, None)
        if not success:
            raise Exception("Failed to register key " + displayWindowKey)

        self.screen = screen
        self.mainWindow = mainWindow

    def _display(self, data):
        self._init()
        self.mainWindow.show_now()

    def window_focused_switch_handler(self, scr, window):
        win = scr.get_active_window()
        if win is not None:
            logger.debug("Selected mainWindow: " + win.get_name())
        self.nav.putWindow(win)

    def window_deleted(self, scr, window):
        logger.debug("Window deleted: " + window.get_name())
        self.nav.removeWindow(window)

    def move_backward(self, data):
        window = self.nav.moveBackward()
        self._selectWnckWindow(window)
        if window is not None:
            logger.debug("Move backward: " + window.get_name())

    def move_forward(self, data):
        window = self.nav.moveForward()

        self._selectWnckWindow(window)
        if window is not None:
            print "Move forward: " + window.get_name()

    def _selectWnckWindow(self, wnck_window):
        if wnck_window:
            timestamp = int(time.time())
            logger.debug("Activating wnck_window: " + wnck_window.get_name())
            workspace = wnck_window.get_workspace()
            workspace.activate(timestamp)
            wnck_window.activate(timestamp)
            self.nav.putWindow(wnck_window)

    def _init(self):
        logger.debug("init")
        wnck_workspace_to_workspace = dict()
        for ws in self.screen.get_workspaces():
            workspace = Workspace(ws.get_name())
            wnck_workspace_to_workspace[ws] = workspace

        for w in self.screen.get_windows():
            win = Window(w.get_name(), w.get_mini_icon(), w)
            if w.get_workspace():
                workspace = wnck_workspace_to_workspace[w.get_workspace()]
                workspace.windows.append(win)

        workspaces = list()
        for ws in self.screen.get_workspaces():
            workspaces.append(wnck_workspace_to_workspace[ws])

        self.mainWindow.setWorkspaces(workspaces)


class WindowManager:
    def __init__(self, window):
        self._window = window

    def display(self, workspaces):
        self._window.setWorkspaces(workspaces)


class Workspace:
    def __init__(self, name):
        self.name = name
        self.windows = list()


class Window:
    def __init__(self, name, icon, window):
        self.name = name
        self.icon = icon
        self.window = window

    def activate(self):
        timestamp = int(time.time())
        logger.debug("Activating wnck_window: " + self.window.get_name())
        workspace = self.window.get_workspace()
        workspace.activate(timestamp)
        self.window.activate(timestamp)

    def isActive(self):
        return self.window.is_active()

    def __str__(self):
        return window.get_name()

logger = common.getLogger("Window")


class MainWindow(gtk.Window):
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
        self.__eventBoxToWindow = {}

    def setWorkspaces(self, workspaces):
        logger.debug("setWorkspaces")
        self.__eventBoxToWindow = {}

        for child in self._table.get_children():
            self._table.remove(child)

        col = 0
        for ws in workspaces:
            row = 1
            header = self._createHeader(ws)
            self._table.attach(header, col, col + 1, 0, 1)
            for win in ws.windows:
                frame = gtk.Frame()
                control = self._createWinControl(win)
                frame.add(control)
                self._table.attach(frame, col, col + 1, row, row + 1)
                row = row + 1
            col = col + 1
        self.set_default_size(-1, -1)
        self.show_all()
        self.present()
        self.set_resizable(False)

    def _key_press_event(self, sender, eventData):
        logger.debug("_key_press_event" + str(eventData))
        if eventData.keyval == gtk.keysyms.Escape:
            self.hide()

    def _focus_changed(self, sender, data):
        self.hide()

    def _createWinControl(self, win):
        hbox = gtk.HBox()
        labelText = win.name.decode('utf-8')
        if(win.isActive()):
            label = gtk.Label("<b>" + labelText[:30] + "</b>")
        else:
            label = gtk.Label(labelText[:30])

        label.set_use_markup(True)
        label.set_tooltip_text(win.name)
        eventBox = gtk.EventBox()
        self.__eventBoxToWindow[eventBox] = win

        eventBox.add(label)
        eventBox.connect("button-press-event", self._on_button_press_event)

        pixmap = gtk.Image()
        pixmap.set_from_pixbuf(win.icon)
        hbox.pack_start(pixmap, False, False)

        hbox.pack_start(eventBox, True, True)
        return hbox

    def _createHeader(self, workspace):
        label = gtk.Label()
        label.set_text("Workspace: " + workspace.name)
        return label

    def _on_button_press_event(self, sender, eventData):
        win = self.__eventBoxToWindow[sender]
        win.activate()

if __name__ == '__main__':
    logger.debug("Starting application...")
    window = MainWindow()
    manager = KeyboardManager(Navigator(),
                              Configuration(),
                              wnck.screen_get_default(),
                              window)
    app = App(window)
    app.start()
