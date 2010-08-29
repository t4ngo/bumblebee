
from pyutilib.component.core    import Interface


#===========================================================================

class ICommandSet(Interface):

    def get_name_description(self):
        """
            Return a (name, description) 2-tuple describing the command set.

            The name must be a short, single line string.  The description
            may span multiple lines.

        """

    def get_commands(self):
        """
            Return a tuple of commands within this command set.

            Each command returned must implement that ICommand interface.

        """

    def load(self):
        """ Load the command set. """

    def unload(self):
        """ Unload the command set. """


#---------------------------------------------------------------------------

class ICommandSetLoader(Interface):

    def update(self):
        """
            Called at short intervals allowing the command set loader to
            load and/or unload any added/removed command sets.

        """


#---------------------------------------------------------------------------

class ICommandSetObserver(Interface):

    def loaded_command_set(self, command_set):
        """ Called when a command set has been loaded. """

    def unloaded_command_set(self, command_set):
        """ Called when a command set has been unloaded. """
