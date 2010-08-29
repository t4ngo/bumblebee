
import sys
import logging
import wx
import dragonfly

from .log_panel                 import LogPanel
from .grammar_panel             import GrammarPanel


#===========================================================================

class MainFrame(wx.Frame):

    def __init__(self, parent, id, title):
        initial_size = (800, 500)
        wx.Frame.__init__(self, parent, id, title, size=initial_size)

        # Create main frame's menu structure.
        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        menu = wx.Menu()
        menubar.Append(menu, "&File")
        mi_exit = menu.Append(-1, "E&xit\tAlt-X",
                              "Close window and exit Bumblebee.")
        self.Bind(wx.EVT_MENU, self.on_close, mi_exit)

        menu = wx.Menu()
        menubar.Append(menu, "&Help")
        mi_about = menu.Append(-1, "About",
                               "Show information about Bumblebee.")
        self.Bind(wx.EVT_MENU, self.on_about, mi_about)

        self._panel = MainPanel(self, -1)

        self.Centre()
        self.Show(True)

    def on_close(self, event):
        self.Destroy()

    def on_about(self, event):
        something


#---------------------------------------------------------------------------

class MainPanel(wx.Panel):

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        sizer = wx.BoxSizer()
        self.SetSizer(sizer)

        notebook = wx.Notebook(self)
        sizer.Add(notebook, 1, wx.EXPAND)

        log_page = LogPanel(notebook, -1)
        notebook.AddPage(log_page, "Log")

        grammar_page = GrammarPanel(notebook, -1)
        notebook.AddPage(grammar_page, "Grammars")
