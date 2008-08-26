#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pysvnmanager.hooks.plugins import *
from pysvnmanager.hooks.plugins import _

class EolStyleCheck(PluginBase):

    # Brief name for this plugin.
    name = _("mime-type and eol-style check")
    
    # Longer description for this plugin.
    description = _("New file must provide svn:eol-style if not binary file.")
    
    # Hooks-plugin type: T_START_COMMIT, ..., T_POST_UNLOCK
    type = T_PRE_COMMIT
    
    # Plugin config option/value in config ini file.
    key = "check_eol_style"
    value = "yes"
    
    def enabled(self):
        """
        Return True, if this plugin has been setup.
        Simply call 'has_config()'.
        """
        return self.has_config()
    
    def get_detail(self):
        """
        Show detail informantion if plugin is already installed.
        """
        return self.description
    
    def install_config_form(self):
        """
        This method will be called to build setup configuration form.
        If this plugin needs parameters, provides form fields here.
        Any html and javascript are welcome.
        
        Default: just output description.
        """
        return super(EolStyleCheck, self).install_config_form()
        
    def uninstall(self):
        """
        Uninstall hooks-plugin from repository.
        Simply call 'unset_config()' and 'save()'.
        """
        self.unset_config()
        self.save()
    
    def install(self, params=None):
        """
        Install hooks-plugin from repository.
        Simply call 'set_config()' and 'save()'.
        
        Form fields in setup_config() will pass as params.
        """
        self.set_config()
        self.save()
        
def execute(repospath=""):
    """
    Generate and return a hooks plugin object

    @param request: repos full path
    @rtype: Plugin
    @return: Plugin object
    """
    return EolStyleCheck(repospath)