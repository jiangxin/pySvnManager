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
from pysvnmanager.model import hooks as _hooks

log = logging.getLogger(__name__)

class ReposController(BaseController):
    requires_auth = True
    
    def __init__(self):
        self.authz = SvnAuthz(cfg.authz_file)
        self.login_as = session.get('user')
        # Used as checked in user to rcs file.
        self.authz.login_as = self.login_as
        
        self.repos_root = cfg.repos_root
        self.repos = _repos.Repos(self.repos_root)
        self.repos_list = self.repos.repos_list


    def __before__(self, action):
        super(ReposController, self).__before__(action)
        if not self.authz.is_super_user(self.login_as):
            return redirect_to(h.url_for(controller='security', action='failed'))
        
    def index(self):
        return render('/repos/hooks.mako')

    def init_repos_list(self):
        filter = request.params.get('filter')
        total = 0;
        msg = ''
 
        # get javascript code for top_form's role_selector
        msg += 'id[0]="%s";' % '...'
        msg += 'name[0]="%s";\n' % _("Please choose...")
        total += 1;
        for reposname in self.repos_list:
            if filter=='blank' and not self.repos.is_blank_svn_repos(reposname):
                continue
            msg += 'id[%d]="%s";' % (total, reposname)
            msg += 'name[%d]="%s";\n' % (total, reposname)
            total += 1;
        msg += 'total=%d;\n' % total
        return msg

    def get_plugin_list(self):
        reposname = request.params.get('select')
        h = _hooks.Hooks(self.repos_root + '/' + reposname)
        total = 0;
        msg = ''
 
        # get javascript code for top_form's role_selector
        msg += 'id[0]="%s";' % '...'
        msg += 'name[0]="%s";\n' % _("Please choose...")
        total += 1;
        for name in h.unapplied_plugins:
            msg += 'id[%d]="%s";' % (total, name)
            msg += 'name[%d]="%s";\n' % (total, name + ': ' + h.plugins[name].name)
            total += 1;
        msg += 'total=%d;\n' % total
        
        return msg
    
    def get_installed_hook_form(self):
        reposname = request.params.get('select')
        h = _hooks.Hooks(self.repos_root + '/' + reposname)
        msg = ''
        if len(h.applied_plugins) > 0:
            msg += _("Installed hooks:")
            msg += "<br>\n"
            num = 0
            
            msg += "<table class='hidden'>\n"
            msg += "<tr><th align='left'></th>" + \
                    "<th align='left'>" + _("Id") + "</th>" + \
                    "<th align='left'>" + _("Plugin name") + "</th>" + \
                    "<th align='left'>" + _("Type") + "</th>" + \
                    "</tr>\n"
            for name in h.applied_plugins:
                msg += "<tr><td width='1' rolspan='2'>"
                msg += '<input type="checkbox" name="pluginid_%(num)d" value="%(plugin)s">' % {
                    'num': num, 'plugin': name, }
                msg += "</td>\n"
                msg += "<td><a href='#' onclick=\"show_hook_config_form('%s'); return false;\">" % name + name + "</a></td>\n"
                msg += "<td>" + h.plugins[name].name + "</td>\n"
                msg += "<td>" + h.plugins[name].get_type() + "</td>\n"
                msg += "</tr>\n"
                msg += "<tr><td></td><td colspan='3'>" + h.plugins[name].show_install_info() + "</td></tr>\n"
                num += 1
            msg += "</table>\n"
            msg += '<input type="submit" name="uninstall_hook" value="%s">\n' % _("Remove selected hooks")

        return msg
    
    def get_hook_setting_form(self):
        reposname  = request.params.get('repos')
        pluginname = request.params.get('plugin')
        h = _hooks.Hooks(self.repos_root + '/' + reposname)
        result  = "<input type='hidden' name='_repos' value='%s'>" % reposname
        result += "<input type='hidden' name='_plugin' value='%s'>" % pluginname
        result +=  h.plugins[pluginname].show_install_config_form()

        return result
    
    def setup_hook(self):
        try:
            d = request.params
            reposname = d.get("_repos")
            pluginname = d.get("_plugin")
            h = _hooks.Hooks(self.repos_root + '/' + reposname)
            plugin = h.plugins[pluginname]
            plugin.install(d)
        except Exception, e:
            result = "<div class='error'>" + _("Apply plugin '%(plugin)s' on '%(repos)s' Failed. Error message:<br>\n%(msg)s") % {
                        "plugin": pluginname, "repos":reposname, "msg": except_to_unicode(e) } + "</div>"
        else:
            result = "<div class='info'>" + _("Apply plugin '%(plugin)s' on '%(repos)s' success.") % {
                        "plugin": pluginname, "repos":reposname} + "</div>"
        return result
    
    def uninstall_hook(self):
        plugin_list=[]
        d = request.params
        reposname = d.get("_repos")
        for i in d.keys():
            if "pluginid_" in i:
                plugin_list.append(d[i])

        if plugin_list:
            log.debug("plugin_list:" + ','.join(plugin_list))
            try:
                hookobj = _hooks.Hooks(self.repos_root + '/' + reposname)
                for pluginname in plugin_list:
                    hookobj.plugins[pluginname].reload()
                    hookobj.plugins[pluginname].uninstall()
                    log.info("my delete plugin %s, %s" % (pluginname, hookobj.plugins[pluginname].name))
            except Exception, e:
                result = "<div class='error'>" + _("Delete plugin '%(plugin)s' on '%(repos)s' Failed. Error message:<br>\n%(msg)s") % {
                        "plugin": ", ".join(plugin_list), "repos":reposname, "msg": except_to_unicode(e) } + "</div>"
            else:
                result = "<div class='info'>" + _("Delete plugin '%(plugin)s' on '%(repos)s' success.") % {
                        "plugin": ", ".join(plugin_list), "repos":reposname} + "</div>"
        else:
            result = "<div class='error'>" + _("No plugin has been deleted for '%(repos)s'.") % {"repos":reposname} + "</div>"
        return result

    def create_submit(self):
        try:
            d = request.params
            reposname = d.get("reposname")
            self.repos.create(reposname)
        except Exception, e:
            result = "<div class='error'>" + _("Create repository '%(repos)s' Failed. Error message:<br>\n%(msg)s") % {
                        "repos":reposname, "msg": except_to_unicode(e) } + "</div>"
        else:
            result = "<div class='info'>" + _("Create repository '%(repos)s' success.") % {"repos":reposname} + "</div>"
        return result
        
    def create(self):
        return render('/repos/create.mako')


    def remove_submit(self):
        try:
            d = request.params
            reposname = d.get("repos_list")
            self.repos.delete(reposname)
        except Exception, e:
            result = "<div class='error'>" + _("Delete repository '%(repos)s' Failed. Error message:<br>\n%(msg)s") % {
                        "repos":reposname, "msg": except_to_unicode(e) } + "</div>"
        else:
            result = "<div class='info'>" + _("Delete blank repository '%(repos)s' success.") % {"repos":reposname} + "</div>"
        return result
    
    def remove(self):
        return render('/repos/remove.mako')
