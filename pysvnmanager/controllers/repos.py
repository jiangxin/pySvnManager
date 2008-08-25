# -*- coding: utf-8 -*-
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
        total = 0;
        msg = ''
 
        # get javascript code for top_form's role_selector
        msg += 'id[0]="%s";' % '...'
        msg += 'name[0]="%s";\n' % _("Please choose...")
        total += 1;
        for reposname in self.repos_list:
            msg += 'id[%d]="%s";' % (total, reposname)
            msg += 'name[%d]="%s";\n' % (total, reposname)
            total += 1;
        msg += 'total=%d;\n' % total
        msg += 'revision="%s";\n' % self.authz.version
        return msg

    def get_plugin_list(self):
        reposname = request.params.get('select')        
        h = _hooks.Hooks(self.repos_root + reposname)
        total = 0;
        msg = ''
 
        # get javascript code for top_form's role_selector
        msg += 'id[0]="%s";' % '...'
        msg += 'name[0]="%s";\n' % _("Please choose...")
        total += 1;
        for name in h.unapplied_plugins.keys():
            msg += 'id[%d]="%s";' % (total, name)
            msg += 'name[%d]="%s";\n' % (total, h.plugins[name].name)
            total += 1;
        msg += 'total=%d;\n' % total
        
        return msg
    
    def get_remove_hook_form_content(self):
        reposname = request.params.get('select')        
        h = _hooks.Hooks(self.repos_root + reposname)
        msg = ''
        if len(h.applied_plugins) > 0:
            msg += "Installed hooks:"
            msg += "<br>\n"
            num = 0
 
            for name in h.applied_plugins.keys():
                msg += '<input type="checkbox" name="pluginid_%(num)d" value="%(plugin)s">' % {
                    'num': num, 'plugin': name, }
                desc = h.plugins[name].description
                detail = h.plugins[name].detail
                msg += '%(plugin)s - %(desc)s' % {
                    'plugin': name, 'name': h.plugins[name].name, 'desc': desc, }
                if detail and detail != desc:
                    msg += ' - %(detail)s' % { 'detail': detail, }
                msg += '<br>\n'
            msg += '<input type="submit" name="remove_hook" value="Remove selected hooks">\n'

        return msg
    
    def get_hook_form(self):
        reposname  = request.params.get('repos')
        pluginname = request.params.get('plugin')
        h = _hooks.Hooks(self.repos_root + reposname)

        return h.plugins[pluginname].show_form()
    
    def apply_new_hook(self):
        try:
            d = request.params
            reposname = d.get("_repos")
            pluginname = d.get("_plugin")
            h = _hooks.Hooks(self.repos_root + reposname)
            plugin = h.plugins[pluginname]
            plugin.set_plugin(d)
        except Exception, e:
            result = "Apply plugin '%(plugin)s on '%(repos)s' Failed. Error message:<br>\n%(msg)s" % {
                        "plugin": pluginname, "repos":reposname, "msg": e}
        else:
            result = "Apply plugin '%(plugin)s on '%(repos)s' success." % {
                        "plugin": pluginname, "repos":reposname}
        return result
    
    def remove_hook(self):
        try:
            d = request.params
            reposname = d.get("_repos")
            h = _hooks.Hooks(self.repos_root + reposname)
            for i in d.keys():
                if "pluginid_" in i:
                    pluginname = d[i]
                    plugin = h.plugins[pluginname]
                    plugin.delete_plugin()
        except Exception, e:
            result = "Delete plugin '%(plugin)s on '%(repos)s' Failed. Error message:<br>\n%(msg)s" % {
                        "plugin": pluginname, "repos":reposname, "msg": e}
        else:
            result = "Delete plugin '%(plugin)s on '%(repos)s' success." % {
                        "plugin": pluginname, "repos":reposname}
        return result
    
    def create(self):
        return render('/repos/create.mako')

    def remove(self):
        return render('/repos/remove.mako')
