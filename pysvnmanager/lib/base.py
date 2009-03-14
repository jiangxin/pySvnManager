# -*- coding: utf-8 -*-
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

"""The base Controller API

Provides the BaseController class for subclassing.
"""
from pylons.controllers import WSGIController
from pylons.templating import render_mako as render

from pylons import c, cache, config, g, request, response, session
from pylons.controllers.util import abort, etag_cache, redirect_to
from pylons.decorators import jsonify, validate
from pylons.i18n import _, ungettext, N_
from pylons.i18n import set_lang, add_fallback
import pysvnmanager.lib.helpers as h
import pysvnmanager.model as model

import sys
config_path = config["here"] + '/config'
if config_path not in sys.path:
    sys.path.insert(0, config_path)
from localconfig import LocalConfig as cfg

#import logging
#log = logging.getLogger(__name__)

class BaseController(WSGIController):
    requires_auth = []

    def __before__(self, action):
        
        if 'lang' in session:
            set_lang(session['lang'])
        #log.debug(request.languages)
        for lang in request.languages:
            if lang.lower() in ['zh-cn', 'zh']:
                add_fallback('zh')
            elif lang in ['en']:
                add_fallback(lang)

        if isinstance(self.requires_auth, bool) and not self.requires_auth:
            pass
        elif isinstance(self.requires_auth, (list, tuple)) and \
            not action in self.requires_auth:
            pass
        else:
            if 'user' not in session:
                session['path_before_login'] = request.path_info
                session.save()
                return redirect_to(h.url_for(controller='security'))

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        return WSGIController.__call__(self, environ, start_response)

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
