
import sys
import logging
import csv
import wx
import dragonfly

from .log_control import LogListCtrl


#===========================================================================

class LogPanel(wx.Panel):

    _log = logging.getLogger("LogPanel")

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        # Create the log panel's main sizer.
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Create the log messages control and register it with Python's
        #  logging infrastructure.
        self._log_control = LogListCtrl(self)
        sizer.Add(self._log_control, 1, wx.EXPAND)
        self._log_control.setup_logging()

        # Create controls for working with the log messages.
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button_sizer, 0, flag=wx.ALIGN_RIGHT)

        export_button = wx.Button(self, -1, "Export")
        button_sizer.Add(export_button, 0, flag=wx.TOP | wx.RIGHT, border=2)
        self.Bind(wx.EVT_BUTTON, self.on_export, export_button)

    def on_export(self, event):
        wildcard = ("CSV files (*.csv)|*.csv"
                    "|Text files (*.txt)|*.txt"
                    "|All files|*.*")
        dialog = wx.FileDialog(self, "Export destination",
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                               wildcard=wildcard)
        if dialog.ShowModal() != wx.ID_OK:
            dialog.Destroy()
            self._log.debug("Export canceled by user.")
            return

        destination_path = dialog.GetPath()

        try:
            destination_file = open(destination_path, "wb")
        except Exception, e:
            self._log.exception("Failed to open export file {0}: {1}."
                                "".format(destination_path, e))
            return

        try:
            writer = csv.writer(destination_file)
            messages = self._log_control.get_messages()
            writer.writerows(messages)
        except Exception, e:
            self._log.exception("Failed to export to file {0}: {1}."
                                "".format(destination_path, e))
            return

        self._log.error("Log exported to {0}".format(destination_path))
