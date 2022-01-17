# Copyright (C) 2012-13 Nick Boultbee, Thomas Vogt
# Copyright (C) 2008 Andreas Bombe
# Copyright (C) 2005  Michael Urman
# Based on osd.py (C) 2005 Ton van den Heuvel, Joe Wreshnig
#                 (C) 2004 Gustavo J. A. M. Carneiro
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from quodlibet.plugins import (PluginConfig, ConfProp, IntConfProp,
    FloatConfProp, ColorConfProp)


DEFAULT_PATTERN = "\n".join((
    "<album|<album><part| - <part>><tracknumber| · <tracknumber>>>",
    "[span weight='bold' size='large']<title>[/span]",
    "<albumartist|<albumartist>|<artist|<artist>|No artist>>")
)

def get_config(prefix):
    class FSDConfig:

        plugin_conf = PluginConfig(prefix)

        font = ConfProp(plugin_conf, "font", "Sans 22")
        string = ConfProp(plugin_conf, "string", DEFAULT_PATTERN)
        monitor = IntConfProp(plugin_conf, "monitor", 0)
        coversize = IntConfProp(plugin_conf, "coversize", 400)

    return FSDConfig()
