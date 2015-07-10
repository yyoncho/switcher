'''
Created on Jan 1, 2011

@author: kyoncho
'''
import time
import keybinder
import ui
import wnck
from _Application import _Application as App

import common

logger = common.getLogger("default")


FORWARD_KEY = "<ctrl><alt>f"
BACKWARD_KEY = "<ctrl><alt>b"


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
        else:
            if self._back:
                ret = self._back[0]
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
        logger.debug("(back=%s) (forward=%s)" %
                     (len(self._back), len(self._forward)))


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
            if w.get_workspace():
                win = Window(w.get_name(), w.get_mini_icon())
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
    def __init__(self, name, icon):
        self.name = name
        self.icon = icon


if __name__ == '__main__':
    logger.debug("Starting application")
    window = ui.Window()
    manager = KeyboardManager(Navigator(),
                              Configuration(),
                              wnck.screen_get_default(),
                              window)
    app = App(window)
    app.start()
