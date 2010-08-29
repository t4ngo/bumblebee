
import sys
import time
import math
import logging
import ast
import wx
import dragonfly
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import codegen


#===========================================================================

class TimerObserver(dragonfly.RecognitionObserver):
    """
        Recognition observer that pauses the timer of an action dialog
        during recognition processing.

    """

    def __init__(self, parent):
        dragonfly.RecognitionObserver.__init__(self)
        self._parent = parent

    def on_begin(self):
        self._parent.pause_timer()

    def on_recognition(self, words):
        self._parent.unpause_timer()

    def on_failure(self):
        self._parent.unpause_timer()


#---------------------------------------------------------------------------

class ActionDialogBase(wx.Frame):
    """
        GUI dialog allowing a user to interact with a Dragonfly action
        before it's executed.

    """

    def __init__(self, parent, title, interval=3.0):
        self._title = title
        wx.Frame.__init__(self, parent, -1, title)
        self._log = logging.getLogger("gui.action_dialog")
        self.Bind(wx.EVT_CLOSE, self.on_close)

        root_panel = wx.Panel(self, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add panel to contain custom controls are derived class.
        child_panel = wx.Panel(root_panel, -1)
        sizer.Add(child_panel, 1, wx.EXPAND, 5)

        # Allow derived class to populate its panel.
        self.populate_panel(child_panel)

        sizer.Add((-1, 20))

        # Add timer controls.
        timer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(timer_sizer, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 5)

        timer_gauge_sizer = wx.BoxSizer(wx.VERTICAL)
        timer_sizer.Add(timer_gauge_sizer, 1,
                        wx.LEFT | wx.RIGHT | wx.EXPAND, 5)

        gauge_timer = wx.Gauge(root_panel, -1,
                               style=wx.GA_HORIZONTAL, size=(-1, 12))
        timer_gauge_sizer.Add(gauge_timer, 0, wx.EXPAND)
        self._gauge_timer = gauge_timer

        self._timer_text = wx.StaticText(root_panel, -1, "...")
        timer_gauge_sizer.Add(self._timer_text, 0, flag=wx.ALIGN_CENTER)

        button_stop = wx.Button(root_panel, -1, "Stop")
        timer_sizer.Add(button_stop, 0)
        self.Bind(wx.EVT_BUTTON, self.on_stop, button_stop)
        self._button_stop = button_stop

        # Add buttons.
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button_sizer, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_RIGHT, 5)

        button_ok = wx.Button(root_panel, -1, "OK")
        button_sizer.Add(button_ok, 0, wx.BOTTOM, 5)
        self.Bind(wx.EVT_BUTTON, self.on_ok, button_ok)

        button_cancel = wx.Button(root_panel, -1, "Cancel")
        button_sizer.Add(button_cancel, 0, wx.RIGHT, 5)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, button_cancel)

        root_panel.SetSizer(sizer)
        sizer.Fit(self)
        self.SetMinSize(sizer.GetMinSize())
        self.Centre()
        self.Show(True)
        self.Raise()

        # Start timer.
        self._timer = wx.Timer(self)
        self._timer_state = "stopped"
        if isinstance(interval, (float, int)) and interval > 0:
            timer_duration = interval
            self._timer_interval = 0.02
            timer_steps = timer_duration / self._timer_interval
            self._gauge_timer.SetRange(timer_steps)
            self.Bind(wx.EVT_TIMER, self.on_timer)
            self._timer = wx.Timer(self)
            self._timer.Start(self._timer_interval * 1000, oneShot=False)
            self._timer_state = "running"

        self._observer = TimerObserver(self)
        self._observer.register()

    def pause_timer(self):
        if "stopped" == self._timer_state:
            return
        self._timer_state = "paused"
        self._timer.Stop()

    def unpause_timer(self):
        if "paused" != self._timer_state:
            return
        self._timer_state = "running"
        self._timer.Start(self._timer_interval * 1000, oneShot=False)

    def stop_timer(self):
        self._timer_state = "stopped"
        self._timer.Stop()
        self._button_stop.Disable()
        self._timer_text.SetLabel("Stopped")
        self._gauge_timer.SetValue(0)

    def execute_action(self):
        self.Close()
        time.sleep(0.1)
        self._execute_action()

    def _execute_action(self):
        pass

    def populate_panel(self, panel):
        raise NotImplementedError

    def on_ok(self, event):
        self.execute_action()

    def on_cancel(self, event):
        self.Close()

    def on_timer(self, event):
        current = self._gauge_timer.GetValue() + 1
        max = self._gauge_timer.GetRange()
        if current < max:
            self._gauge_timer.SetValue(current)
            current_label = self._timer_text.GetLabel()
            remaining_seconds = (max - current) * self._timer_interval
            remaining_seconds = math.ceil(remaining_seconds)
            new_label = "{0:.0f} sec".format(remaining_seconds)
            if current_label != new_label:
                self._timer_text.SetLabel(new_label)
        else:
            self._gauge_timer.SetValue(max)
            self._timer.Stop()
            self.execute_action()

    def on_stop(self, event):
        self.stop_timer()

    def on_close(self, event):
        try:
            self._observer.unregister()
        except Exception, e:
            self._log.exception("on_close(): {0}".format(e))
        self.Destroy()


#---------------------------------------------------------------------------

class StringActionDialog(ActionDialogBase):

    def __init__(self, parent, title, data_key, action):
        ActionDialogBase.__init__(self, parent, title)
        self._data_key = data_key
        self._action = action

    def populate_panel(self, panel):
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(panel, -1, self._title + ":")
        sizer.Add(label, flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)

        self.value = wx.TextCtrl(panel, -1)
        sizer.Add(self.value, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
        self.Bind(wx.EVT_TEXT, self.on_text_change, self.value)
        self._first_text_change = True

        panel.SetSizer(sizer)

    def on_text_change(self, event):
        if self._first_text_change:
            self._first_text_change = False
        else:
            self.stop_timer()

    def _execute_action(self):
        data = {self._data_key: self.value.GetValue()}
        self._action.execute(data)


#---------------------------------------------------------------------------

class ActionDialog(dragonfly.ActionBase):

    def __init__(self, title, data_key, action):
        dragonfly.ActionBase.__init__(self)
        self._title = title
        self._data_key = data_key
        self._action = action

    def _execute(self, data=None):
        value = data.get(self._data_key)
        dialog = ScringActionDialog(self._title, self._data_key, value,
                                    self._action)
