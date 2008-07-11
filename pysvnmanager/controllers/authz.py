# -*- coding: utf-8 -*-
import logging

from pysvnmanager.lib.base import *
from pysvnmanager.model.svnauthz import *

log = logging.getLogger(__name__)

class AuthzController(BaseController):
    requires_auth = True

    def __init__(self):
        self.authz = SvnAuthz(cfg.authz_file)
        self.login_as = session.get('user')
        
        c.revision = self.authz.version

        self.reposlist = self.authz.get_manageable_repos_list(self.login_as)
        c.reposlist = self.reposlist
        
        all_avail_users = []
        all_avail_users.append([_("All users(with anon)"), '*'])
        all_avail_users.append([_("Known users"), '$authenticated'])
        all_avail_users.append([_("Anonymous"), '$anonymous'])
        for group in self.authz.grouplist:
            i = group.uname
            if i == '*' or i =='$authenticated' or i == '$anonymous':
                continue
            if i[0] == '@':
                all_avail_users.append([_("Group:")+i[1:], i])
            else:
                all_avail_users.append([i, i])
        for alias in self.authz.aliaslist:
            i = alias.uname
            if i[0] == '&':
                all_avail_users.append([_("Alias:")+i[1:], i])
            else:
                all_avail_users.append([i, i])
        for user in self.authz.userlist:
            i = user.uname
            all_avail_users.append([i, i])
        
        c.all_avail_users = all_avail_users

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

        return render('/authz/index.mako')

    def init_repos_list(self):
        if self.__auth_failed():
            return render('/auth_failed.mako')

        total = 0;
        msg = ''
 
        # get javascript code for top_form's role_selector
        msg += 'id[0]="%s";' % '...'
        msg += 'name[0]="%s";\n' % _("Please choose...")
        total += 1;
        for reposname in self.reposlist:
            msg += 'id[%d]="%s";' % (total, reposname)
            msg += 'name[%d]="%s";\n' % (total, reposname)
            total += 1;
        msg += 'total=%d;\n' % total
        msg += 'revision="%s";\n' % self.authz.version
        return msg

    def repos_changed(self):
        if self.__auth_failed():
            return render('/auth_failed.mako')

        total = 0;
        msg = ''
        d = request.params
        select = d.get('select')
        repos = self.authz.get_repos(select)
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
        msg += 'admin_users="%s";\n' % repos.admins
        msg += 'revision="%s";\n' % self.authz.version
        
        return msg

    def path_changed(self):
        if self.__auth_failed():
            return render('/auth_failed.mako')

        total = 0;
        msg = ''
 
        d = request.params
        reposname = d.get('reposname')
        path = d.get('path')

        module = self.authz.get_module(reposname, path)
        if not module:
            return msg;

        # get javascript code for top_form's role_selector
        for rule in module:
            rule = unicode(rule)
            tmp = rule.split('=')
            msg += 'user[%d]="%s";\n' % (total, tmp[0].strip())
            msg += 'rights[%d]="%s";\n' % (total, tmp[1].strip())
            total += 1;
        msg += 'total=%d;\n' % total
        msg += 'revision="%s";\n' % self.authz.version

        return msg
        
    def save_authz(self):
        if self.__auth_failed():
            return render('/auth_failed.mako')

        d = request.params
        
        member_list = []
        msg = ""

        reposname = d.get('reposname')
        admins    = d.get('admins', '')
        path      = d.get('path')
        rules     = d.get('rules')
        # mode1: new or edit repository
        mode1     = d.get('mode1')
        # mode2: new or edit module
        mode2     = d.get('mode2')
        revision  = d.get('revision', self.authz.version)
        
        try:
            if mode1 == "new":
                repos = self.authz.add_repos(reposname)
            else:
                repos = self.authz.get_repos(reposname)
            if not repos:
                raise Exception, _("Repository %s not exist.") % reposname
            
            if path:
                if mode2 == "new":
                    module = self.authz.add_module(reposname, path)
                else:
                    module = self.authz.get_module(reposname, path)
                if not module:
                    raise Exception, _("Module %s not exist.") % path
            else:
                module = None
            
            if not self.authz.is_admin(self.login_as, repos.name, admins) and \
                not (repos.name != '/' and self.authz.is_super_user(self.login_as)):
                raise Exception, _("You can not delete yourself from admin list.")
            
            self.authz.set_admin(admins, repos)

            if module:
                self.authz.set_rules(reposname, path, rules);
            self.authz.save(revision)
        except Exception, e:
            msg = unicode(e)

        log.info(_("User %(user)s changed authz rules. (rev:%(rev)s,%(msg)s)") % \
                 {'user':session.get('user'), 'rev': revision, 'msg': msg} )
        
        return msg

    def delete_authz(self):
        if self.__auth_failed():
            return render('/auth_failed.mako')

        d = request.params
        
        member_list = []
        msg = ""

        reposname = d.get('reposname')
        path  = d.get('path')
        revision  = d.get('revision', self.authz.version)
        
        try:
            self.authz.del_module(reposname, path);
            self.authz.save(revision)
        except Exception, e:
            msg = unicode(e)
        
        log.info(_("User %(user)s delete authz rules. (rev:%(rev)s,%(msg)s)") % \
                 {'user':session.get('user'), 'rev': revision, 'msg': msg} )

        return msg

