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

class EolStyleCheck(PluginBase):

    # Brief name for this plugin.
    name = _("mime-type and eol-style check")
    
    # Both description and detail are reStructuredText format. 
    # Reference about reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html

    # Short description for this plugin.
    description = _("New file must provide svn:eol-style if not binary file.")
    
    # Long description for this plugin.
    detail = ""
    
    # Hooks-plugin type: T_START_COMMIT, ..., T_POST_UNLOCK
    type = T_PRE_COMMIT
    
    # Plugin config option/value in config ini file.
    key_switch = "eol_style_check"
    key_force  = "eol_style_check_force"
    
    section = 'pre_commit'
    
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
            force = self.get_config(self.key_force)
            if force == "no":
                result += "- " + _("Loose mode: permit checkin without svn:eol-style properity if no CRLF in text file.")
            else:
                result += "- " + _("Strict mode: must have svn:eol-style even if not CRLF in text file.")

        return result
 
    
    def install_config_form(self):
        """
        This method will be called to build setup configuration form.
        If this plugin needs parameters, provides form fields here.
        Any html and javascript are welcome.
        """
        if self.get_config(self.key_force)=="no":
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
        result += "<input type='radio' name='force' value='yes' " + \
                enable_checked  + ">" + _("Strict mode") + "&nbsp;"
        result += "\n<dd>"
        result += _("Must set svn:eol-style even if CRLF not in text file (in Unix format).")
        result += "\n<dt>"
        result += "<input type='radio' name='force' value='no' " + \
                disable_checked + ">" + _("Loose mode") + "<br>"
        result += "\n<dd>"
        result += _("Permit checkin without svn:eol-style properity if is in Unix file format (no crlf in text file).")
        result += "\n</dl>"
        result += "</blockquote>"
        return result
        
    def uninstall(self):
        """
        Uninstall hooks-plugin from repository.
        Simply call 'unset_config()' and 'save()'.
        """
        self.unset_config(self.key_switch)
        self.unset_config(self.key_force)
        self.save()
    
    def install(self, params=None):
        """
        Install hooks-plugin from repository.
        Simply call 'set_config()' and 'save()'.
        
        Form fields in setup_config() will pass as params.
        """
        force = params.get('force', 'no')
        if force != 'no':
            force = 'yes'
        self.set_config(self.key_switch, 'yes')
        self.set_config(self.key_force, force)
        self.save()
        
def execute(repospath=""):
    """
    Generate and return a hooks plugin object

    @param request: repos full path
    @rtype: Plugin
    @return: Plugin object
    """
    return EolStyleCheck(repospath)
