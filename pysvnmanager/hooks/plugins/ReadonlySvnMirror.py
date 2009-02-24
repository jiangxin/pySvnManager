#!/usr/bin/env python
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

from pysvnmanager.hooks.plugins import *
from pysvnmanager.hooks.plugins import _

class ReadonlySvnMirror(PluginBase):

    # Brief name for this plugin.
    name = _("Subversion readonly mirror")
    
    # Both description and detail are reStructuredText format. 
    # Reference about reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html

    # Short description for this plugin.
    description = _("This subversion repository is a svnsync readonly mirror. "
                    "Nobody can checkin, except the svnsync admin user.")
    
    # Long description for this plugin.
    detail = _("Commit to the remote svn server, this repository is a readonly svn mirror."
               "It is the svnsync admin's duty to synchronize svnsync server and mirror.")
    
    # Hooks-plugin type: T_START_COMMIT, ..., T_POST_UNLOCK
    type = T_START_COMMIT
    
    # Plugin config option/value in config ini file.
    key_switch = "mirror_readonly"
    key_admin = "mirror_admin"
    
    section = "start_commit"
    
    def enabled(self):
        """
        Return True, if this plugin has been installed.
        Simply call 'has_config()'.
        """
        return self.has_config(self.key_switch)
    
    def install_info(self):
        """
        Show configurations if plugin is already installed.
        
        return reStructuredText.
        reST reference: http://docutils.sourceforge.net/docs/user/rst/quickref.html
        """
        result = self.description
        if self.enabled():
            result += "\n\n"
            result += "**" + _("Current configuration") + "**\n\n"
            if self.get_config(self.key_switch) == "yes":
                result += "- " + _("Readonly mirror enabled.")
            else:
                result += "- " + _("Readonly mirror disabled.")
            result += "\n"
            admin = self.get_config(self.key_admin)
            if admin:
                result += "- " + _("Admin user: ") + "``" + self.get_config(self.key_admin) + "``"

        return result
    
    def install_config_form(self):
        """
        This method will be called to build setup configuration form.
        If this plugin needs parameters, provides form fields here.
        Any html and javascript are welcome.
        """
        if self.get_config(self.key_switch)=="no":
            enable_checked  = ""
            disable_checked = "checked"
        else:
            enable_checked  = "checked"
            disable_checked = ""

        result = ""
        result += "<p><strong>%s</strong></p>" % _("Fill this form")
        result += "<blockquote>"
        result += "<dl>"
        result += "\n<dt>"
        result += _("Enable readonly mirror: ")
        result += "\n<dd>"
        result += "<input type='radio' name='switch' value='yes' " + \
                enable_checked  + ">" + _("Enable") + "&nbsp;"
        result += "<input type='radio' name='switch' value='no' " + \
                disable_checked + ">" + _("Disable") + "<br>"
        result += "\n<dt>"
        result += _("Svnsync administrator: ")
        result += "\n<dd>"
        result += "<input type='text' name='admin' size='18' value='%s'>" % \
                self.get_config(self.key_admin)
        result += "\n</dl>"
        result += "</blockquote>"
        return result
        
    def uninstall(self):
        """
        Uninstall hooks-plugin from repository.
        Simply call 'unset_config()' and 'save()'.
        """
        self.unset_config(self.key_admin)
        self.unset_config(self.key_switch)
        self.save()
    
    def install(self, params=None):
        """
        Install hooks-plugin from repository.
        Simply call 'set_config()' and 'save()'.
        
        Form fields in setup_config() will pass as params.
        """
        switch = params.get('switch', 'yes')
        if switch != 'yes':
            switch = 'no'
        admin = params.get('admin')
        if not admin:
            switch = 'no'
        self.set_config(self.key_switch, switch)
        self.set_config(self.key_admin, admin)
        self.save()
        
def execute(repospath=""):
    """
    Generate and return a hooks plugin object

    @param request: repos full path
    @rtype: Plugin
    @return: Plugin object
    """
    return ReadonlySvnMirror(repospath)
