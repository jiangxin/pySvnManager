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
from webhelpers.util import html_escape

class SvnSyncMaster(PluginBase):

    # Brief name for this plugin.
    name = _("Sync with downstream svn mirrors")
    
    # Both description and detail are reStructuredText format. 
    # Reference about reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html

    # Short description for this plugin.
    description = _("This subversion repository is a svnsync master server. "
                    "Each new commit will propagate to downstream svn mirrors.")
    
    # Long description for this plugin.
    detail = _("This master svn repository maybe configured with one or several svn mirrors."
               "You must give the url svn mirrors (one with each line), and give the username "
               "and password who initiates the mirror task.")
    
    # Hooks-plugin type: T_START_COMMIT, ..., T_POST_UNLOCK
    type = T_POST_COMMIT
    
    # Plugin config option/value in config ini file.
    key_switch = "mirror_enabled"
    key_username = "mirror_username"
    key_password = "mirror_password"
    key_urls = "mirror_urls"
    
    section = "mirror"
    
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
                result += "- " + _("Mirror enabled.")
            else:
                result += "- " + _("Mirror disabled.")
            result += "\n"
            username = self.get_config(self.key_username)
            if username:
                result += "- " + _("Svnsync username:") + " ``" + username + "``"
            result += "\n"
            urls = self.get_config(self.key_urls)
            if urls:
                result += "- " + _("Url of downstream svn mirrors:") + "\n\n"
                for url in urls.split(';'):
                    result += "  * ``" + url + "``" + "\n"

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
        result += _("Enable svn repo mirror: ")
        result += "\n<dd>"
        result += "<input type='radio' name='switch' value='yes' " + \
                enable_checked  + ">" + _("Enable") + "&nbsp;"
        result += "<input type='radio' name='switch' value='no' " + \
                disable_checked + ">" + _("Disable") + "<br>"
        result += "\n<dt>"
        result += _("Svnsync username:")
        result += "\n<dd>"
        result += "<input type='text' name='username' size='18' value='%s'>" % \
                self.get_config(self.key_username)
        result += "\n<dt>"
        result += _("Svnsync password:")
        result += "\n<dd>"
        result += "<input type='password' name='password' size='18' value='%s'>" % \
                self.get_config(self.key_password)
        result += "\n<dt>"
        result += _("Url of downstream svn mirrors:")
        result += "\n<dd>"
        result += "<textarea name='urls' rows='3' cols='40'>"
        result += html_escape( "\n".join( self.get_config(self.key_urls).split(';') ) )
        result += "</textarea>"

        result += "\n</dl>"
        result += "</blockquote>"
        return result
        
    def uninstall(self):
        """
        Uninstall hooks-plugin from repository.
        Simply call 'unset_config()' and 'save()'.
        """
        self.unset_config(self.key_username)
        self.unset_config(self.key_password)
        self.unset_config(self.key_switch)
        self.unset_config(self.key_urls)
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
        username = params.get('username')
        password = params.get('password')
        urls     = params.get('urls')
        if urls:
            urls = ';'.join( urls.splitlines() )
        else:
            urls = ''
        if urls == '':
            switch = 'no'
        self.set_config(self.key_switch, switch)
        self.set_config(self.key_username, username)
        self.set_config(self.key_password, password)
        self.set_config(self.key_urls, urls)
        self.save()
        
def execute(repospath=""):
    """
    Generate and return a hooks plugin object

    @param request: repos full path
    @rtype: Plugin
    @return: Plugin object
    """
    return SvnSyncMaster(repospath)
