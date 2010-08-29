
import sys
import time
import math
import logging
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin


#===========================================================================

class LogListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    """
        List control class for storing log messages.

        Log messages are inserted into this class by a
        :class:`LogListHandler` instance.

    """

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)

        # Create columns appropriate for log messages.
        self.InsertColumn(0, "Time", wx.LIST_FORMAT_RIGHT, width=120)
        self.InsertColumn(1, "Level", width=50)
        self.InsertColumn(2, "Logger", width=100)
        self.InsertColumn(3, "Message", width=400)

    def setup_logging(self):
        # Store original streams so that they can be restored later.
        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr

        # Create new stream loggers for capturing output.
        sys.stdout = StreamLogger(logging.getLogger("stdout").info)
        sys.stderr = StreamLogger(logging.getLogger("stderr").warning)

        # Create new log list handler for inserting logging messages
        #  into log list control.
        log = logging.getLogger("")
        log_list_handler = LogListHandler(self)
        log_list_handler.setLevel(logging.DEBUG)
        log.addHandler(log_list_handler)

    def restore_logging(self):
        if hasattr(self, "_old_stdout"):
            sys.stdout = self._old_stdout
        if hasattr(self, "_old_stderr"):
            sys.stderr = self._old_stderr

    def append_record(self, record):
        time_structure = time.localtime(record.created)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time_structure)
        index = self.InsertStringItem(sys.maxint, timestamp)
        self.SetStringItem(index, 1, record.levelname)
        self.SetStringItem(index, 2, record.name)
        self.SetStringItem(index, 3, record.getMessage())

        # Automatically scrawled down, except if items are selected.
        if self.GetSelectedItemCount() == 0:
            self.EnsureVisible(index)

        # Attributes and methods of a record instance:
        #  args, created, exc_info, exc_text, filename, funcName,
        #  getMessage, levelname, levelno, lineno, module, msecs,
        #  msg, name, pathname, process, processName, relativeCreated,
        #  thread, threadName

    def get_messages(self):
        """
            Return a list of tuples, each containing the fields of
            a message in the log list control.

        """

        messages = []
        column_count = self.GetColumnCount()
        for row in range(self.GetItemCount()):
            message = tuple(self.GetItem(row, column).GetText()
                            for column in range(column_count))
            messages.append(message)
        return messages


#===========================================================================

class StreamLogger(object):
    """
        Behaves like a standard Python stream object and passes all
        data written to it to a given function.

    """

    def __init__(self, logger_func):
        """
            Create a new StreamLogger instance.

            :param logger_func: Callable which will be called for each
                block of data written to this StreamLogger instance.
                It is passed a single argument: the data written.

        """
        self._logger_func = logger_func
        self._incomplete_line = None

    def write(self, data):
        if self._incomplete_line:
            data = self._incomplete_line + data
            self._incomplete_line = None
        lines = data.splitlines(True)
        for line in lines[1:]:
            self._logger_func(line[:-1])
        line = lines[-1]
        if "\n" in line:
            self._logger_func(line[:-1])
        else:
            self._incomplete_line = line

    def flush(self):
        pass


#---------------------------------------------------------------------------

class LogListHandler(logging.Handler):
    """
        Handler for Python's standard library logging framework which
        inserts log messages into wxPython list control.

    """

    def __init__(self, list_control, *args, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        self._list_control = list_control

    def emit(self, record):
        # Use wx.CallAfter() to make this operation thread safe.
        wx.CallAfter(self._emit, record)

    def _emit(self, record):
        # Test for truth value of control, because during shutdown
        #  the control can sometimes be destroyed before
        #  this method is called for the last time.
        if self._list_control:
            self._list_control.append_record(record)
