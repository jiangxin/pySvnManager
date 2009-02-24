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
import webhelpers

class CommitLogCheck(PluginBase):

    # Brief name for this plugin.
    name = _("Check commit log message")
    
    # Both description and detail are reStructuredText format. 
    # Reference about reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html

    # Short description for this plugin.
    description = _("User must provide commit-log message when checkin.")

    # Long description for this plugin.
    detail = ""
    
    # Hooks-plugin type: T_START_COMMIT, ..., T_POST_UNLOCK
    type = T_PRE_COMMIT
    
    # Plugin config option/value in config ini file.
    key_switch   = "commit_log_check_enable"
    key_size     = "commit_log_check_size"
    key_permit   = "commit_log_check_permit"
    key_prohibit = "commit_log_check_prohibit"
    
    section = 'pre_commit'
    
    def enabled(self):
        """
        Return True, if this plugin has been installed.
        Simply call 'has_config()'.
        """
        return self.has_config(self.key_switch) and self.has_config(self.key_size)
    
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
                result += "- " + _("Commit log check is enabled.")
            else:
                result += "- " + _("Commit log check is disabled.")
            result += "\n"
            result += "- " + _("Minimal size of commit log: ") + self.get_config(self.key_size)
            result += "\n"
            permit   = self.get_config(self.key_permit)
            prohibit = self.get_config(self.key_prohibit)
            if permit:
                result += "- " + _("Pattern which commit log must match against: ") + permit
                result += "\n"
            if prohibit:
                result += "- " + _("Pattern which commit log must **NOT** match against: ") + prohibit
                result += "\n"
            
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
        result += "\n<dl>"
        result += "\n<dt>"
        result += _("Enable commit log check: ")
        result += "\n<dd>"
        result += "<input type='radio' name='switch' value='yes' " + \
                enable_checked  + ">" + _("Enable") + "&nbsp;"
        result += "<input type='radio' name='switch' value='no' " + \
                disable_checked + ">" + _("Disable")
        result += "\n<dt>"
        result += _("Minimal size of commit log: ")
        result += "\n<dd>"
        result += "<input type='text' name='size' size='5' value=\"%s\">" % \
                webhelpers.util.html_escape(self.get_config(self.key_size))
        result += "\n<dt>"
        result += _("Pattern which commit log must match against: ")
        result += "\n<dd>"
        result += "<textarea name='permit' rows='3' cols='40'>"
        result += webhelpers.util.html_escape(self.get_config(self.key_permit))
        result += "</textarea>"
        result += "\n<dt>"
        result += _("Pattern which commit log must <b>NOT</b> match against: ")
        result += "\n<dd>"
        result += "<textarea name='prohibit' rows='3' cols='40'>"
        result += webhelpers.util.html_escape(self.get_config(self.key_prohibit))
        result += "</textarea>"
        result += "\n</dl>"
        result += "</blockquote>"
        return result
        
    def uninstall(self):
        """
        Uninstall hooks-plugin from repository.
        Simply call 'unset_config()' and 'save()'.
        """
        self.unset_config(self.key_switch)
        self.unset_config(self.key_size)
        self.unset_config(self.key_permit)
        self.unset_config(self.key_prohibit)
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
        size = params.get('size')
        log.debug("size: %s" % size)
        if int(size)<1:
            raise Exception, _("Commit log size must > 0.")
        permit   = params.get('permit')
        prohibit = params.get('prohibit')
        self.set_config(self.key_switch, switch)
        self.set_config(self.key_size, size)
        self.set_config(self.key_permit, permit)
        self.set_config(self.key_prohibit, prohibit)
        self.save()
        
def execute(repospath=""):
    """
    Generate and return a hooks plugin object

    @param request: repos full path
    @rtype: Plugin
    @return: Plugin object
    """
    return CommitLogCheck(repospath)
