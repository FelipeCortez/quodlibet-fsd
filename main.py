# Copyright (c) 2012,2013,2016 Nick Boultbee
# Copyright (C) 2012-13 Thomas Vogt
# Copyright (C) 2008 Andreas Bombe
# Copyright (C) 2005  Michael Urman
# Based on osd.py (C) 2005 Ton van den Heuvel, Joe Wreshnig
#                 (C) 2004 Gustavo J. A. M. Carneiro
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from gi.repository import Gdk, GLib

from quodlibet import _, app
from quodlibet.plugins.events import EventPlugin
from quodlibet.qltk import Icons
from quodlibet.util import cached_property

from .fsdwindow import FSDWindow
from .config import get_config
from .prefs import FSDPrefs


class FSD(EventPlugin):
    PLUGIN_ID = "FSD"
    PLUGIN_NAME = _("Full-screen display")
    PLUGIN_DESC = _("Displays song information on your screen when it "
                    "changes.")
    PLUGIN_ICON = Icons.DIALOG_INFORMATION

    __current_window = None

    @cached_property
    def Conf(self):
        return get_config('FSD')

    def PluginPreferences(self, parent):
        return FSDPrefs(self)

    def plugin_on_song_started(self, song):
        if self.__current_window is not None:
            self.__current_window.hide()
            self.__current_window.destroy()

        if song is None or app.player.paused:
            self.__current_window = None
            return

        window = FSDWindow(self.Conf, song)
        window.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        window.connect('button-press-event', self.__buttonpress)
        self.__current_window = window

        window.show()

    def plugin_on_error(self, song, error):
        if self.__current_window is not None:
            self.__current_window.destroy()
            self.__current_window = None

    def __buttonpress(self, window, event):
        window.hide()
        if self.__current_window is window:
            self.__current_window = None
        window.destroy()
