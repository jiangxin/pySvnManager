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

        self.reposlist = self.authz.get_manageable_repos_list(self.login_as)
        c.reposlist = self.reposlist
        c.userlist = map(lambda x:x.uname, self.authz.grouplist)
        c.userlist.extend(map(lambda x:x.uname, self.authz.aliaslist))
        c.userlist.extend(map(lambda x:x.uname, self.authz.userlist))
        c.pathlist = []

    def __auth_failed(self, reposname=None):
        if not self.reposlist:
            return True
        elif reposname and not reposname in self.reposlist:
            return True
        else:
            return False
    
    def index(self):
        # Return a rendered template
        #   return render('/some/template.mako')
        # or, Return a response
        if self.__auth_failed():
            return render('/auth_failed.mako')

        return render('/check/index.mako')
    
    def access_map(self):
        if self.__auth_failed():
            return render('/auth_failed.mako')

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
                repos = c.reposlist
            if not '/' in self.reposlist:
                if not repos or \
                    ( isinstance(repos, basestring) and not repos in self.reposlist ):
                    return _("Permission denied.")
            if path and path != "*":
                msglist = self.authz.get_path_access_msgs(username, repos, path, abbr=abbr)
                msg += "<div id='acl_path_msg'>" + "<br>\n".join(msglist) + "</div>"

            msg += "<pre>"+ "\n".join(self.authz.get_access_map_msgs(username, repos, abbr=abbr))+"</pre>"

        return msg
        
    def get_path_options(self, repos=None, type=None, path=None):
        if self.__auth_failed():
            return render('/auth_failed.mako')

        # get params from arguments or from request
        buff = ''
        opts = ''
        if not repos:
            d = request.params
            repos = d.get('repos')
            type = d.get('type', 'select')
            if type == 'manual':
                path = d.get('path')
            else:
                type = 'select'
                path = d.get('path', '...')

        if repos and repos != '...' and repos in self.reposlist:
            pathlist = self.authz.get_repos_path_list(repos)
            opts = u"<option value='*'>%s</option>" % _("All modules")
            for i in pathlist:
                if i == path:
                    selected = 'selected'
                else:
                    selected = ''
                opts += "<option value='%(path)s' %(selected)s>%(path)s</option>" % {'path':i, 'selected':selected}
        
        buff = u'''<input type='radio' name='pathinput' value='select' '''
        if type == 'select':
            buff += ' checked '
        buff += '>'
        buff += _("Select module")
        buff += u'''
<select name="pathselector" size="0" onFocus="select_path(this.form)">
%s
</select>
<br />''' % opts
        
        buff += '''<input type="radio" name="pathinput" value="manual" '''
        if type == 'manual':
            buff += ' checked '
        buff += '>'
        buff += _("Manual input")
        buff += '<input type="text" name="pathname" value="'
        if type == 'manual' and path:
            buff += path
        buff += '" onFocus="edit_path(this.form)">'

        return buff
