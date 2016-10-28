'''
Created on Jan 1, 2011

@author: kyoncho
'''
import time

import keybinder
import gtk
import pango
import wnck
import logging
import sys
from os import getpid
from _Application import _Application as App

streamHandler = logging.StreamHandler(sys.stdout)

loggerConfig = {"Window": logging.DEBUG,
                "default": logging.DEBUG}


def getLogger(name):
    logger = logging.getLogger(name)
    logger.addHandler(streamHandler)
    logger.setLevel(loggerConfig[name])
    return logger


logger = getLogger("default")
FORWARD_KEY = "<ctrl><alt>n"
BACKWARD_KEY = "<ctrl><alt>p"
SHOW_MAIN = "Super_L"


BOLD_TEXT = '<span size="12000"><b>%s</b></span>'
NORMAL_TEXT = '<span size="12000">%s</span>'
LABEL_SIZE = 200

FORWARD = "F"
BACKWARD = "B"

SYMBOLS = map(str, range(1, 10)) + \
          map(chr, range(ord('A'), ord('Z')))


def boldText(text):
    return BOLD_TEXT % (text)


def normalText(text):
    return NORMAL_TEXT % (text)


def getColor(input, key):
    splitItem = lambda x: x.split(": ")
    keyValues = map(splitItem, input.split("\n"))
    result = [x[1] for x in keyValues if x[0] == key]
    return gtk.gdk.color_parse(result[0]) if result else None


class Navigator:
    def __init__(self):
        self._back = list()
        self._forward = list()
        self._windows = list()

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
        self._windows.append(window)

    def removeWindow(self, window):
        if self._back.count(window):
            self._back.remove(window)

        if self._forward.count(window):
            self._forward.remove(window)
            self._printLocal()

    def _printLocal(self):
        logger.debug("back=%s, forward=%s" %
                     (map(self._getWindowName, self._back),
                      map(self._getWindowName, self._forward)))

    def getWindowNumbers(self):
        return self._windows[:10]

    def _getWindowName(self, win):
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
        success = keybinder.bind(forwKey, self._move_forward, None)
        if not success:
            raise Exception("Failed to register key " + forwKey)

        backKey = conf.getConfig("backward")
        success = keybinder.bind(backKey, self._move_backward, None)
        if not success:
            raise Exception("Failed to register key " + backKey)

        displayWindowKey = SHOW_MAIN
        success = keybinder.bind(displayWindowKey, self._display, None)
        if not success:
            raise Exception("Failed to register key " + displayWindowKey)

        self.screen = screen
        self.mainWindow = mainWindow

    def _display(self, data):
        if not self.mainWindow.is_focus():
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

        # refresh the main window if the window is active and in case we
        # are not handling the closing of the main window.
        if not self._isMainWindow(window):
            if self.mainWindow.isVisible:
                self._init()
                self.mainWindow.show_now()
            else:
                logger.debug("Application window is not " +
                             "visible no need to updated.")
        else:
            logger.debug("The application window has been deleted.")

    def _isMainWindow(self, window):
        return getpid() == window.get_pid()

    def _move_backward(self, data):
        window = self.nav.moveBackward()
        self._selectWnckWindow(window)
        if window is not None:
            logger.debug("Move backward: " + window.get_name())

    def _move_forward(self, data):
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

    def _init(self):
        wnck_workspace_to_workspace = dict()
        for ws in self.screen.get_workspaces():
            workspace = Workspace(ws.get_name())
            wnck_workspace_to_workspace[ws] = workspace

        for w in self.screen.get_windows():
            if not self._isMainWindow(w):
                win = Window(w.get_name(), w.get_mini_icon(), w)
                if w.get_workspace():
                    workspace = wnck_workspace_to_workspace[w.get_workspace()]
                    workspace.windows.append(win)

        workspaces = list()
        for ws in self.screen.get_workspaces():
            workspaces.append(wnck_workspace_to_workspace[ws])

        self.mainWindow.setWorkspaces(workspaces)


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

    def close(self):
        logger.debug("Closing window")
        timestamp = int(time.time())
        self.window.close(timestamp)

    def isActive(self):
        return self.window.is_active()

    def __str__(self):
        return window.get_name()

    def __hash__(self):
        return hash((self.window))

    def __eq__(self, other):
        return self.window == other.window


class MainWindow(gtk.Window):
    def __init__(self):
        super(gtk.Window, self).__init__()
        self.set_decorated(False)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_keep_above(True)
        self.connect("key-press-event", self._key_press_event)
        self.connect("focus-out-event", self._focus_changed)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self._table = gtk.Table()
        self.add(self._table)
        self.show_all()
        self._keyToWindow = {}
        self.__selected = None
        self.isVisible = False
        self._predefinedKeys = {}

    def setWorkspaces(self, workspaces):
        logger.debug("setWorkspaces")

        self.__workspaces = workspaces
        self.__eventBoxToWindow = {}
        self.__nuberToWindow = {}

        for child in self._table.get_children():
            self._table.remove(child)

        col = 0
        keyIndex = 0
        self._workspaceLookup = list()
        for ws in workspaces:
            windowsList = list()
            windowsList.append(None)
            self._workspaceLookup.append(windowsList)
            row = 1
            header = self._createHeaderLabel(ws)
            self._table.attach(header, col, col + 1, 0, 1)
            for win in ws.windows:
                if win in self._predefinedKeys:
                    symbol = self._predefinedKeys[win]
                else:
                    symbol = SYMBOLS[keyIndex]
                    keyIndex = keyIndex + 1

                self.__nuberToWindow[symbol] = win

                control = self._createWinControl(win, symbol, win.isActive())

                # keep the selected item
                if(win.isActive()):
                    self.__selected = (row, col, win, control, symbol)

                self._attachControl(col, row, control)

                row = row + 1
                windowsList.append((win, control, symbol))

            col = col + 1
            self.set_default_size(-1, -1)
            self.show_all()
            self.present()
            self.isVisible = True
            self.set_resizable(False)

    def _key_press_event(self, sender, eventData):
        logger.debug("_key_press_event: eventData=" + str(eventData.keyval))
        logger.debug("_key_press_event: eventData=" + str(eventData.state))

        if eventData.state == gtk.gdk.CONTROL_MASK | \
           gtk.gdk.MOD1_MASK | gtk.gdk.SHIFT_MASK:
            # register the shortcut for the current window.
            keyChar = chr(eventData.keyval).lower()
            win = self.__selected[2]
            # first remove the shortcut if the shortcut is already assigned.
            for key, item in self._predefinedKeys.items():
                if item == keyChar:
                    del self._predefinedKeys[key]
            self._predefinedKeys[win] = keyChar
            # update the __selected
            self.__selected = (self.__selected[0],
                               self.__selected[1],
                               self.__selected[2],
                               self.__selected[3],
                               keyChar)

            logger.debug("Registered the following predefined keys: %s",
                         self._predefinedKeys)
            self.setWorkspaces(self.__workspaces)

        elif eventData.state == gtk.gdk.CONTROL_MASK:
            if eventData.keyval == gtk.keysyms.n:
                self._updateSelected(1, 0)
            elif eventData.keyval == gtk.keysyms.p:
                self._updateSelected(-1, 0)
            elif eventData.keyval == gtk.keysyms.f:
                self._updateSelected(0, 1)
            elif eventData.keyval == gtk.keysyms.b:
                self._updateSelected(0, -1)
            elif eventData.keyval == gtk.keysyms.q:
                self.destroy()
            elif eventData.keyval == gtk.keysyms.j:
                w = self.__selected[2]
                w.activate()
        elif eventData.keyval == gtk.keysyms.Return:
            w = self.__selected[2]
            w.activate()
        elif eventData.keyval == gtk.keysyms.Escape:
            self.hide()
        elif eventData.keyval == gtk.keysyms.Tab:
            pass
        elif eventData.keyval == gtk.keysyms.Down:
            self._updateSelected(1, 0)
        elif eventData.keyval == gtk.keysyms.Up:
            self._updateSelected(-1, 0)
        elif eventData.keyval == gtk.keysyms.Left:
            self._updateSelected(0, -1)
        elif eventData.keyval == gtk.keysyms.Right:
            self._updateSelected(0, 1)
        elif eventData.keyval == gtk.keysyms.Delete:
            w = self.__selected[2]
            w.close()
        else:
            if eventData.keyval < 256:
                key = chr(eventData.keyval)
                if key in self.__nuberToWindow:
                    win = self.__nuberToWindow[key]
                    win.activate()

    def _focus_changed(self, sender, data):
        self.isVisible = False
        self.hide()

    def _updateSelected(self, vertical, horizontal):

        logger.debug("Updating selected %s %s, selection data = %s" %
                     (vertical, horizontal, self.__selected))
        windowIndex, workspaceIndex, win, current, symbol = self.__selected

        newWindowIndex, newWorkspaceIndex = self.__calculateSelected(
            windowIndex, workspaceIndex, vertical, horizontal)

        logger.debug(
            "Selecting window with index (%s, %s) old indexes = (%s, %s)" %
            (newWorkspaceIndex, newWindowIndex, workspaceIndex, windowIndex))

        # deselect the old item
        self._table.remove(current)
        updated = self._createWinControl(win, symbol, False)
        self._attachControl(workspaceIndex, windowIndex, updated)

        # select the new item
        newWindow, oldControl, symbol = self._workspaceLookup[
            newWorkspaceIndex][newWindowIndex]

        logger.debug("New window = " + str(newWindow))

        self._table.remove(oldControl)
        selectedControl = self._createWinControl(newWindow,
                                                 symbol,
                                                 True)
        self._attachControl(newWorkspaceIndex,
                            newWindowIndex,
                            selectedControl)
        # update selected
        self.__selected = (newWindowIndex,
                           newWorkspaceIndex,
                           newWindow,
                           selectedControl,
                           symbol)

        # update the view
        self.show_all()
        self.present()

    def __calculateSelected(self, windowIndex, wsIndex, vertical, horizontal):
        logger.debug(
            "windowIndex = %s, wsIndex = %s, vertical = %s, horizontal = %s",
            windowIndex, wsIndex, vertical, horizontal)
        newWsIndex = wsIndex + horizontal
        endOfWs = len(self._workspaceLookup) <= newWsIndex or newWsIndex < 0
        if not endOfWs:
            ws = self._workspaceLookup[newWsIndex]
            newWindowIndex = windowIndex + vertical
            if not len(ws) <= newWindowIndex and newWindowIndex > 0:
                return newWindowIndex, newWsIndex
            else:
                windowIndex = 0 if newWindowIndex > 0 else len(ws)
                return self.__calculateSelected(
                    windowIndex, wsIndex, vertical, horizontal)
        elif endOfWs:
            wsIndex = -1 if newWsIndex >= 0 else len(self._workspaceLookup)
            return self.__calculateSelected(
                windowIndex, wsIndex, vertical, horizontal)

    def _attachControl(self, workspaceIndex, windowIndex, control):
        self._table.attach(control,
                           workspaceIndex, workspaceIndex + 1,
                           windowIndex, windowIndex + 1)

    def _createWinControl(self, win, key, isActive):
        hbox = gtk.HBox()

        eventBox = gtk.EventBox()
        self.__eventBoxToWindow[eventBox] = win

        eventBox.add(self._createWindowLabel(win, key))
        eventBox.connect("button-press-event", self._on_button_press_event)

        if isActive:
            eventBox.modify_bg(gtk.STATE_NORMAL,
                               self._getSelectedColor())

        pixmap = gtk.Image()
        pixmap.set_from_pixbuf(win.icon)
        hbox.pack_start(pixmap, False, False)
        hbox.pack_start(eventBox, True, True)

        result = gtk.Frame()
        result.add(hbox)
        return result

    def _createHeaderLabel(self, workspace):
        label = gtk.Label()
        label.set_size_request(LABEL_SIZE, -1)
        label.set_text(boldText(workspace.name))
        label.set_use_markup(True)
        return label

    def _on_button_press_event(self, sender, eventData):
        win = self.__eventBoxToWindow[sender]
        win.activate()

    def _createWindowLabel(self, win, key):
        utf8Name = win.name.decode('utf-8')
        withKey = "<b>%s</b> %s" % (key, utf8Name)

        text = boldText(withKey) if win.isActive() else normalText(withKey)

        label = gtk.Label(text)
        label.set_alignment(0, 0.5)
        label.set_use_markup(True)
        label.set_tooltip_text(win.name)
        label.set_ellipsize(pango.ELLIPSIZE_END)
        label.set_size_request(LABEL_SIZE, -1)
        return label

    def _getSelectedColor(self):
        settings = gtk.settings_get_default()
        colorScheme = settings.get_property("gtk-color-scheme")
        return getColor(colorScheme, "selected_bg_color")

if __name__ == '__main__':
    logger.debug("Starting application...")
    window = MainWindow()
    manager = KeyboardManager(Navigator(),
                              Configuration(),
                              wnck.screen_get_default(),
                              window)
    app = App(window)
    window.connect("destroy", app.destroy)
    app.start()
