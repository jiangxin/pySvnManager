"""The base Controller API

Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""
from pylons import c, cache, config, g, request, response, session
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, etag_cache, redirect_to
from pylons.decorators import jsonify, validate
from pylons.i18n import _, ungettext, N_
from pylons.templating import render
from pylons.i18n import set_lang, add_fallback
import pysvnmanager.lib.helpers as h
import pysvnmanager.model as model

import sys
config_path = config["here"] + '/config'
if config_path not in sys.path:
    sys.path.insert(0, config_path)
from localconfig import LocalConfig as cfg

class BaseController(WSGIController):
    requires_auth = []

    def __before__(self, action):
        
        if 'lang' in session:
            set_lang(session['lang'])
        for lang in request.languages:
            if lang in ['zh', 'en']:
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
                return redirect_to(h.url_for(controller='login'))

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        return WSGIController.__call__(self, environ, start_response)

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
