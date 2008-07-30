# -*- coding: utf-8 -*-
import logging

from pysvnmanager.lib.base import *
from pysvnmanager.model.svnauthz import *

log = logging.getLogger(__name__)

class CheckController(BaseController):
    requires_auth = True

    def __init__(self):
        self.authz = SvnAuthz(cfg.authz_file)
        self.login_as = session.get('user')
        # Used as checked in user to rcs file.
        self.authz.login_as = self.login_as
        self.reposlist = self.authz.get_manageable_repos_list(self.login_as)

    def __before__(self, action):
        super(CheckController, self).__before__(action)
        if not self.reposlist:
            return redirect_to(h.url_for(controller='security', action='failed'))
        
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
