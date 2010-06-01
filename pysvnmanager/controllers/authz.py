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
from pysvnmanager.lib.text import to_unicode
from pysvnmanager.model.svnauthz import *
from pysvnmanager.model import repos as _repos
from pylons.i18n import _, ungettext, N_

log = logging.getLogger(__name__)

class AuthzController(BaseController):
    requires_auth = True

    def __init__(self):
        try:
            self.authz = SvnAuthz(cfg.authz_file)
            self.login_as = session.get('user')
            # Used as checked in user to rcs file.
            self.authz.login_as = self.login_as
            self.own_reposlist = set(self.authz.get_manageable_repos_list(self.login_as))
            
            # self.reposlist_new is what in ReposRoot directory.
            self.all_reposlist = set(_repos.Repos(cfg.repos_root).repos_list)
            self.all_reposlist.add('/')
            
            self.reposlist_set = self.own_reposlist & self.all_reposlist
            self.reposlist_unexist = self.own_reposlist - self.all_reposlist
            
            self.is_super_user = self.authz.is_super_user(self.login_as)
            if self.is_super_user:
                self.reposlist_unset = self.all_reposlist - self.own_reposlist
            else:
                self.reposlist_unset = set()
        except Exception, e:
            import traceback
            g.catch_e = [unicode(e), traceback.format_exc(5) ]
            return
            
    def __before__(self, action=None):
        super(AuthzController, self).__before__(action)
        if not self.own_reposlist and not self.is_super_user:
            return redirect(url(controller='security', action='failed'))
        diff = self.authz.differ()
        if diff:
            c.global_message = _('Some one maybe you, has modified the svn authz file by hands. Please save once to fix possible config error.') + "<blockquote>" + "<br>".join(diff.splitlines()) + "</blockquote>"

    def index(self):
        c.revision = self.authz.version
        c.is_super_user = self.is_super_user
        # used for functional test.
        c.reposlist = self.own_reposlist
        all_avail_users = []
        all_avail_users.append([_("All users(with anon)"), '*'])
        all_avail_users.append([_("Known users"), '$authenticated'])
        all_avail_users.append([_("Anonymous"), '$anonymous'])
        for group in self.authz.grouplist:
            i = group.uname
            if i == '*' or i =='$authenticated' or i == '$anonymous':
                continue
            all_avail_users.append([_("Group:")+i[1:], i])
        for alias in self.authz.aliaslist:
            i = alias.uname
            all_avail_users.append([_("Alias:")+i[1:], i])
        for user in self.authz.userlist:
            i = user.uname
            all_avail_users.append([i, i])
        
        c.all_avail_users = all_avail_users

        return render('/authz/index.mako')

    def init_repos_list(self):
        total = 0;
        msg = ''
 
        # get javascript code for top_form's role_selector
        msg += 'id[0]="%s";' % '...'
        msg += 'name[0]="%s";\n' % _("Please choose...")
        total += 1;
        for reposname in sorted(self.reposlist_set):
            msg += 'id[%d]="%s";' % (total, reposname)
            msg += 'name[%d]="%s";\n' % (total, reposname)
            total += 1;
        for reposname in sorted(self.reposlist_unexist):
            msg += 'id[%d]="%s";' % (total, reposname)
            msg += 'name[%d]="%s";\n' % (total, reposname+' (?)')
            total += 1;
        for reposname in sorted(self.reposlist_unset):
            msg += 'id[%d]="%s";' % (total, reposname)
            msg += 'name[%d]="%s";\n' % (total, reposname+' (!)')
            total += 1;
        msg += 'total=%d;\n' % total
        msg += 'revision="%s";\n' % self.authz.version
        return msg

    def repos_changed(self):
        total = 0;
        msg = ''
        d = request.params
        select = d.get('select')
        repos = self.authz.get_repos(select)
        if not repos:
            log.warning("Repos '%s' not exists. Create authz config automatically." % select)
            repos = self.authz.add_repos(select)

        if repos:
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
        d = request.params
        
        member_list = []
        msg = ""

        reposname = d.get('reposname')
        admins    = d.get('admins', '')
        path      = d.get('path')
        rules     = d.get('rules')
        revision  = d.get('revision', self.authz.version)
        
        # mode1: new or edit repository
        mode1     = d.get('mode1')
        if mode1 == "new":
            isAddRepos = True
        else:
            isAddRepos = False
        
        # mode2: new or edit module
        mode2     = d.get('mode2')
        if mode2 == "new":
            isAddModule = True
        else:
            isAddModule = False

        log_message = _(u"User %(user)s changed authz rules. (rev:%(rev)s)") % \
                 {'user':session.get('user'), 'rev': revision}

        try:
            if isAddRepos:
                assert self.is_super_user
                repos = self.authz.add_repos(reposname)
            else:
                repos = self.authz.get_repos(reposname)
                if not repos:
                    assert self.is_super_user
                    log.warning("Repos '%s' not exists. Create authz config automatically." % reposname)
                    repos = self.authz.add_repos(reposname)
                
            if not repos:
                raise Exception, _("Repository %s not exist.") % reposname
            
            if path:
                if isAddModule:
                    module = repos.add_module(path)
                else:
                    module = repos.get_module(path)
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
            self.authz.save(revision, comment=log_message)
        except Exception, e:
            msg = to_unicode(e)

        log.info(log_message)
        if msg: log.error(msg)
        
        return msg

    def delete_authz(self):
        d = request.params
        
        member_list = []
        msg = ""

        reposname = d.get('reposname')
        path  = d.get('path')
        revision  = d.get('revision', self.authz.version)
        
        log_message = _(u"User %(user)s delete authz rules. (rev:%(rev)s)") % \
                         {'user':session.get('user'), 'rev': revision}
        try:
            self.authz.del_module(reposname, path);
            self.authz.save(revision, comment=log_message)
        except Exception, e:
            msg = to_unicode(e)
        
        log.info(log_message)
        if msg: log.error(msg)

        return msg

