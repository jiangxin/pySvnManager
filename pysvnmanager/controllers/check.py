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

import logging

from pysvnmanager.lib.base import *
from pysvnmanager.model.svnauthz import *
from pysvnmanager.model import repos as _repos
from pylons.i18n import _, ungettext, N_

log = logging.getLogger(__name__)

class CheckController(BaseController):
    requires_auth = True

    def __init__(self):
        c.menu_active = "check"
        try:
            self.authz = SvnAuthz(cfg.authz_file)
            self.login_as = session.get('user')
            # Used as checked in user to rcs file.
            self.authz.login_as = self.login_as
            self.reposlist = self.authz.get_manageable_repos_list(self.login_as)
            if self.authz.is_super_user(self.login_as):
                for i in _repos.Repos(cfg.repos_root).repos_list:
                    if i not in self.reposlist:
                        self.reposlist.append(i)
                self.reposlist = sorted(self.reposlist)
        except Exception, e:
            import traceback
            g.catch_e = [unicode(e), traceback.format_exc(5) ]
            return

    def __before__(self, action=None):
        super(CheckController, self).__before__(action)
        if not self.reposlist:
            return redirect(url(controller='security', action='failed'))
        diff = self.authz.differ()
        if diff:
            c.global_message = _('Some one maybe you, has modified the svn authz file by hands. Please save once to fix possible config error.') + "<blockquote>" + "<br>".join(diff.splitlines()) + "</blockquote>"
        
    def index(self):
        c.reposlist = self.reposlist
        c.userlist = map(lambda x:x.uname, self.authz.grouplist)
        c.userlist.extend(map(lambda x:x.uname, self.authz.aliaslist))
        c.userlist.extend(map(lambda x:x.uname, self.authz.userlist))
        c.pathlist = []
        return render('/check/index.mako')
    
    def access_map(self):
        msg = ""
        d = request.params
        
        if d.get('userinput') == 'manual':
            username = d.get('username')
        else:
            username = d.get('userselector')

        if d.get('reposinput') == 'manual':
            repos = d.get('reposname')
        else:
            repos = d.get('reposselector')

        if d.get('pathinput') == 'manual':
            path = d.get('pathname')
        else:
            path = d.get('pathselector')

        abbr = d.get('abbr', 'False')
        if abbr.lower() == 'true' or abbr == '1':
            abbr = True
        else:
            abbr = False
        
        if username != '...' and repos != '...':
            if repos == '*':
                repos = self.reposlist
            if not '/' in self.reposlist:
                if not repos or \
                    ( isinstance(repos, basestring) and not repos in self.reposlist ):
                    return _("Permission denied.")
            if path and path != "*":
                msglist = self.authz.get_path_access_msgs(username, repos, path, abbr=abbr)
                msg += "<div id='acl_path_msg'>" + "<br>\n".join(msglist) + "</div>"

            msg += "<pre>"+ "\n".join(self.authz.get_access_map_msgs(username, repos, abbr=abbr))+"</pre>"

        return msg
        
    def get_auth_path(self, repos=None, type=None, path=None):
        total = 0;
        msg = ''
        d = request.params
        reposname = d.get('repos')
        repos = self.authz.get_repos(reposname)
        if not repos:
            return msg;

        # get javascript code for top_form's role_selector
        msg += 'id[0]="%s";' % '...'
        msg += 'name[0]="%s";\n' % _("Please choose...")
        total += 1;
        for path in repos.path_list:
            msg += 'id[%d]="%s";' % (total, path)
            msg += 'name[%d]="%s";\n' % (total, path)
            total += 1;
        msg += 'total=%d;\n' % total
        
        return msg
