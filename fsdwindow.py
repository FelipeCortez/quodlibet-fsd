# Copyright (C) 2012-13 Thomas Vogt
# Copyright (C) 2012-17 Nick Boultbee
# Copyright (C) 2008 Andreas Bombe
# Copyright (C) 2005  Michael Urman
# Based on osd.py (C) 2005 Ton van den Heuvel, Joe Wreshnig
#                 (C) 2004 Gustavo J. A. M. Carneiro
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from collections import namedtuple
from math import pi

import gi
gi.require_version("PangoCairo", "1.0")

from gi.repository import Gtk, GObject, GLib
from gi.repository import Gdk
from gi.repository import Pango, PangoCairo
import cairo

from quodlibet.qltk.image import get_surface_for_pixbuf, get_surface_extents
from quodlibet import qltk
from quodlibet import app
from quodlibet import pattern


class FSDWindow(Gtk.Window):

    MARGIN = 80
    """never any closer to the screen edge than this"""

    BORDER = 100
    """text/cover this far apart, from edge"""

    def __init__(self, conf, song):
        Gtk.Window.__init__(self)

        screen = self.get_screen()
        rgba = screen.get_rgba_visual()
        if rgba is not None:
            self.set_visual(rgba)

        self.conf = conf
        self.iteration_source = None
        self.fading_in = False
        self.fullscreen()

        mgeo = screen.get_monitor_geometry(conf.monitor)
        textwidth = mgeo.width - 2 * (self.BORDER + self.MARGIN)

        scale_factor = self.get_scale_factor()
        cover_pixbuf = app.cover_manager.get_pixbuf(
            song, conf.coversize * scale_factor, conf.coversize * scale_factor)
        coverheight = 0
        coverwidth = 0
        if cover_pixbuf:
            self.cover_surface = get_surface_for_pixbuf(self, cover_pixbuf)
            coverwidth = cover_pixbuf.get_width() // scale_factor
            coverheight = cover_pixbuf.get_height() // scale_factor
            textwidth -= coverwidth + self.BORDER
        else:
            self.cover_surface = None

        layout = self.create_pango_layout('')
        layout.set_alignment(Pango.Alignment.LEFT)
        layout.set_spacing(Pango.SCALE * 7)
        layout.set_font_description(Pango.FontDescription(conf.font))
        try:
            layout.set_markup(pattern.XMLFromMarkupPattern(conf.string) % song)
        except pattern.error:
            layout.set_markup("")

        layout.set_width(Pango.SCALE * textwidth)
        layoutsize = layout.get_pixel_size()
        if layoutsize[0] < textwidth:
            layout.set_width(Pango.SCALE * layoutsize[0])
            layoutsize = layout.get_pixel_size()
        self.title_layout = layout

        rect = namedtuple("Rect", ["x", "y", "width", "height"])

        rect.x = 350
        rect.y = (mgeo.height - coverheight) // 2
        rect.width = coverwidth
        rect.height = coverheight

        self.cover_rectangle = rect

    def do_draw(self, cr):
        if self.is_composited():
            self.draw_title_info(cr)
        else:
            # manual transparency rendering follows
            walloc = self.get_allocation()
            wpos = self.get_position()

            if not getattr(self, "_bg_sf", None):
                # copy the root surface into a temp image surface
                root_win = self.get_root_window()
                bg_sf = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                           walloc.width, walloc.height)
                pb = Gdk.pixbuf_get_from_window(
                    root_win, wpos[0], wpos[1], walloc.width, walloc.height)
                bg_cr = cairo.Context(bg_sf)
                Gdk.cairo_set_source_pixbuf(bg_cr, pb, 0, 0)
                bg_cr.paint()
                self._bg_sf = bg_sf

            if not getattr(self, "_fg_sf", None):
                # draw the window content in another temp surface
                fg_sf = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                           walloc.width, walloc.height)
                fg_cr = cairo.Context(fg_sf)
                fg_cr.set_source_surface(fg_sf)
                self.draw_title_info(fg_cr)
                self._fg_sf = fg_sf

            # first draw the background so we have 'transparancy'
            cr.set_operator(cairo.OPERATOR_SOURCE)
            cr.set_source_surface(self._bg_sf)
            cr.paint()

            # then draw the window content with the right opacity
            cr.set_operator(cairo.OPERATOR_OVER)
            cr.set_source_surface(self._fg_sf)
            cr.paint_with_alpha(self.get_opacity())

    def draw_conf_rect(self, cr, x, y, width, height):
        cr.rectangle(x, y, width, height)

    def draw_title_info(self, cr):
        cr.save()

        self.set_name("osd_bubble")
        qltk.add_css(self, """
            #osd_bubble {
                background-color:rgba(0,0,0,0);
            }
        """)

        cr.set_operator(cairo.OPERATOR_OVER)
        cr.set_source_rgba(0, 0, 0, 1.0)
        self.draw_conf_rect(cr, 0, 0, self.get_size()[0], self.get_size()[1])
        cr.fill()

        textx = 0

        if self.cover_surface is not None:
            rect = self.cover_rectangle
            textx += rect.width + 350 + self.MARGIN
            surface = self.cover_surface
            transmat = cairo.Matrix()

            cr.set_source_surface(surface, 0, 0)
            width, height = get_surface_extents(surface)[2:]

            transmat.scale(width / float(rect.width),
                           height / float(rect.height))
            transmat.translate(-rect.x, -rect.y)
            cr.get_source().set_matrix(transmat)
            self.draw_conf_rect(cr,
                                rect.x, rect.y,
                                rect.width, rect.height)
            cr.fill()

        PangoCairo.update_layout(cr, self.title_layout)
        height = self.title_layout.get_pixel_size()[1]
        texty = (self.get_size()[1] - height) // 2

        cr.set_source_rgb(1, 1, 1)
        cr.move_to(textx, texty)
        PangoCairo.show_layout(cr, self.title_layout)
        cr.restore()
