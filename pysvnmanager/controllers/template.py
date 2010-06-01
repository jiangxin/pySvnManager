# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 OpenSourceXpress Ltd. (http://www.ossxp.com)
# Author: Jiang Xin
# Contact: http://www.ossxp.com
#          http://www.worldhello.net
#          http://moinmo.in/JiangXin
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from pysvnmanager.lib.base import *
from pylons.i18n import _, ungettext, N_

class TemplateController(BaseController):

    def __init__(self):
        ## To prevent redirect loop
        if g.catch_e:
            self.catch_e = g.catch_e[:]
            g.catch_e = None
        else:
            self.catch_e = None

    def view(self, url):
        """By default, the final controller tried to fulfill the request
        when no other routes match. It may be used to display a template
        when all else fails, e.g.::

            def view(self, url):
                return render('/%s' % url)

        Or if you're using Mako and want to explicitly send a 404 (Not
        Found) response code when the requested template doesn't exist::

            import mako.exceptions

            def view(self, url):
                try:
                    return render('/%s' % url)
                except mako.exceptions.TopLevelLookupException:
                    abort(404)

        By default this controller aborts the request with a 404 (Not
        Found)
        """
        abort(404)

    def show_e(self):
        if self.catch_e:
            c.catch_e = self.catch_e
        else:
            c.catch_e = ['', '']
        return render('/catch_e.mako')

