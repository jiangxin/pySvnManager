#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pysvnmanager.hooks.plugins import *
from pysvnmanager.hooks.plugins import _

class AllowRevpropChange(PluginBase):

    # Brief name for this plugin.
    name = _("Allow revprop change")
    
    # Both description and detail are reStructuredText format. 
    # Reference about reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html

    # Short description for this plugin.
    description = _("Allow user change commit-log or other rev-properties.")
    
    # Long description for this plugin.
    detail = _("Commit-log is the only rev-prop we allow to change. "
               "Because the changes of rev-prop can not be reverted back, "
               "administrator must setup email notification to record this "
               "irreversible action.")
    
    # Hooks-plugin type: T_START_COMMIT, ..., T_POST_UNLOCK
    type = T_PRE_REVPROP_CHANGE
    
    # Plugin config option/value in config ini file.
    key = "revprop_change_enable"
    value = "yes"
    
    section = 'pre_revprop_change'
    
    def enabled(self):
        """
        Return True, if this plugin has been installed.
        Simply call 'has_config()'.
        """
        return self.has_config()
    
    def install_info(self):
        """
        Show configurations if plugin is already installed.
        
        return reStructuredText.
        reST reference: http://docutils.sourceforge.net/docs/user/rst/quickref.html
        """
        return self.description
    
    def install_config_form(self):
        """
        This method will be called to build setup configuration form.
        If this plugin needs parameters, provides form fields here.
        Any html and javascript are welcome.
        """
        return ""
        
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
    return AllowRevpropChange(repospath)
