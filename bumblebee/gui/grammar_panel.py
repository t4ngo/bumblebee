
import sys
import logging
import wx
import dragonfly
import pyutilib.component.core
from pyutilib.component.core    import Plugin, implements

from ..command.interface        import ICommandSet, ICommandSetObserver


#===========================================================================

class GrammarPanel(wx.Panel):

    _log = logging.getLogger("GrammarPanel")

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        sizer = wx.BoxSizer()
        self.SetSizer(sizer)

        grammar_tree = GrammarTree(self, -1)
        sizer.Add(grammar_tree, 1, wx.EXPAND)


#---------------------------------------------------------------------------

class GrammarTree(wx.TreeCtrl):

    _log = logging.getLogger("GrammarTree")

    def __init__(self, parent, id):
        wx.TreeCtrl.__init__(self, parent, id)
        self._command_sets = None
        GrammarTreeUpdater(self).update()

    def update(self, command_sets=None):
        self._log.debug("update({0})".format(command_sets))
        if command_sets != None and self._command_sets == command_sets:
            # If nothing has changed, return immediately.
            return
        self._command_sets = command_sets

        self.DeleteAllItems()

        # If no command sets are available, report so clearly.
        if not self._command_sets:
            root = self.AddRoot("No command sets loaded")
            return

        sorting_func = lambda cmds: cmds.get_name_description()[0]
        sorted_command_sets = sorted(self._command_sets, key=sorting_func)

        root = self.AddRoot("Command sets")
        for command_set in sorted_command_sets:
            name, description = command_set.get_name_description()
            node = self.AppendItem(root, name)
            for command in command_set.get_commands():
                self.AppendItem(node, command.name)

        self.Expand(root)


#---------------------------------------------------------------------------

class GrammarTreeUpdater(Plugin):

    implements(ICommandSetObserver)

    def __init__(self, grammar_tree):
        self._grammar_tree = grammar_tree

    def loaded_command_set(self, command_set):
        self.update()

    def unloaded_command_set(self, command_set):
        self.update()

    def update(self):
        command_sets = pyutilib.component.core.ExtensionPoint(ICommandSet)
        self._grammar_tree.update(tuple(command_sets))
