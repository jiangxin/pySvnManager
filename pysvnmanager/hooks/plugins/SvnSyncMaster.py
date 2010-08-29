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
from subprocess import Popen, PIPE, STDOUT
import re

SVNCMD = "LC_ALL=C svn --non-interactive --no-auth-cache --trust-server-cert "
SVNSYNCCMD = "LC_ALL=C svnsync --non-interactive --no-auth-cache --trust-server-cert "

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

    passwd_re = re.compile(r"(password|passwd)[\s=]+\S+")

    def strip_password(self, command):
        return self.passwd_re.sub("password=**********", command)
    
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

        if switch != 'no':
            self.svnsync_init(urls, username, password)

        self.set_config(self.key_switch, switch)
        self.set_config(self.key_username, username)
        self.set_config(self.key_password, password)
        self.set_config(self.key_urls, urls)
        self.save()

    def svnsync_init(self, urls, username, password):
        def svn_info(url, username, password):
            if username and password:
                command = SVNCMD + "info %(url)s --username %(username)s --password %(password)s" % locals()
            else:
                command = SVNCMD + "info %(url)s" % locals()
            proc = Popen( command, stdout=PIPE, stderr=STDOUT, close_fds=True, shell=True )
            output = proc.communicate()[0]
            if proc.returncode != 0:
                log.error("Failed when execute: %s\n\tgenerate warnings with returncode %d." % (self.strip_password(command), proc.returncode))
                if output:
                    log.error( "Command output:\n" + output )
                raise Exception("Mirror %(url)s can not access. Detail: %(output)s." % locals())
            else:
                log.debug( "command: %s" % self.strip_password(command) )
                if output:
                    log.debug( "output:\n" + output )
            return SVN_INFO(output)

        def svn_revprop0(url, username, password): 
            if username and password:
                command = SVNCMD + "pl -v -r0 --revprop %(url)s --username %(username)s --password %(password)s" % locals()
            else:
                command = SVNCMD + "pl -v -r0 --revprop %(url)s" % locals()
            proc = Popen( command, stdout=PIPE, stderr=STDOUT, close_fds=True, shell=True )
            output = proc.communicate()[0]
            if proc.returncode != 0:
                log.error("Failed when execute: %s\n\tgenerate warnings with returncode %d." % (self.strip_password(command), proc.returncode))
                if output:
                    log.error( "Command output:\n" + output )
                raise Exception("Revprop of mirror %(url)s can not access. Detail: %(output)s." % locals())
            else:
                log.debug( "command: %s" % self.strip_password(command) )
                if output:
                    log.debug( "output:\n" + output )
            return SVN_SYNC_INFO(output)

        sinfo = svn_info("file://"+self.repos, None, None)
        for url in urls.split(';'):
            cmdlist = []
            # if mirror SVN can not access, exception raised.
            dinfo = svn_info(url, username, password)

            # UUID matched?
            if sinfo.uuid != dinfo.uuid:
                raise Exception("UUID not matched, %s not like a mirror." % url)
            uuid = sinfo.uuid

            sync_info = svn_revprop0(url, username, password)

            # Sync not initialized, initiate it now.
            srcurl = "file://" + self.repos
            if sync_info.sync_url is None:

                if dinfo.rev is None or int(dinfo.rev) == 0:
                    if username and password:
                        cmdlist.append( SVNSYNCCMD + "init %(url)s %(srcurl)s --sync-username %(username)s --sync-password %(password)s" % locals() )
                    else:
                        cmdlist.append( SVNSYNCCMD + "init %(url)s %(srcurl)s" % locals() )
                else:
                    newrev = dinfo.rev
                    if username and password:
                        cmdlist.append( SVNCMD + "ps --revprop -r0 svn:sync-last-merged-rev %(newrev)s %(url)s --username %(username)s --password %(password)s" % locals() )
                        cmdlist.append( SVNCMD + "ps --revprop -r0 svn:sync-from-url %(srcurl)s %(url)s --username %(username)s --password %(password)s" % locals() )
                        cmdlist.append( SVNCMD + "ps --revprop -r0 svn:sync-from-uuid %(uuid)s %(url)s --username %(username)s --password %(password)s" % locals() )
                    else:
                        cmdlist.append( SVNCMD + "ps --revprop -r0 svn:sync-last-merged-rev %(newrev)s %(url)s" % locals() )
                        cmdlist.append( SVNCMD + "ps --revprop -r0 svn:sync-from-url %(srcurl)s %(url)s" % locals() )
                        cmdlist.append( SVNCMD + "ps --revprop -r0 svn:sync-from-uuid %(uuid)s %(url)s" % locals() )

            # sync_info.sync_url is not srcurl, reset it to srcurl
            elif sync_info.sync_url and sync_info.sync_url != srcurl:
                if username and password:
                    cmdlist.append( SVNCMD + "ps --revprop -r0 svn:sync-from-url %(srcurl)s %(url)s --username %(username)s --password %(password)s" % locals() )
                else:
                    cmdlist.append( SVNCMD + "ps --revprop -r0 svn:sync-from-url %(srcurl)s %(url)s" % locals() )
            for command in cmdlist:
                proc = Popen( command, stdout=PIPE, stderr=STDOUT, close_fds=True, shell=True )
                output = proc.communicate()[0]
                if proc.returncode != 0:
                    log.error("Failed when execute: %s\n\tgenerate warnings with returncode %d." % (self.strip_password(command), proc.returncode))
                    if output:
                        log.error( "Command output:\n" + output )
                    raise Exception("Failed when execute: %(command)s\n   Detail: %(output)s." % {
                                    'command': self.strip_password(command), 'output': output } )
                else:
                    log.debug( "command: %s" % self.strip_password(command) )
                    if output:
                        log.debug( "output:\n" + output )


class SVN_INFO(object):
    def __init__(self, output):
        self.url = None
        self.root = None
        self.uuid = None
        self.rev = None

        if output:
            self.parse(output)

    def parse(self, output):
        if output:
            if isinstance(output, (str, unicode)):
                output = output.splitlines()
            for line in output:
                if line.startswith("URL:"):
                    self.url = line.split(':',1)[1].strip()
                elif line.startswith("Repository Root:"):
                    self.root = line.split(':',1)[1].strip()
                elif line.startswith("Repository UUID:"):
                    self.uuid = line.split(':',1)[1].strip()
                elif line.startswith("Revision:"):
                    self.rev = line.split(':',1)[1].strip()


class SVN_SYNC_INFO(object):
    def __init__(self, output):
        self.sync_url = None
        self.sync_uuid = None
        self.sync_rev = None

        if output:
            self.parse(output)

    def parse(self, output):
        if output:
            if isinstance(output, (str, unicode)):
                output = output.splitlines()
            i = 0
            while True:
                if i >= len(output):
                    break
                if output[i].strip().startswith("svn:sync-from-uuid"):
                    i+=1
                    self.sync_uuid = output[i].strip()
                elif output[i].strip().startswith("sync-last-merged-rev"):
                    i+=1
                    self.sync_rev = output[i].strip()
                elif output[i].strip().startswith("svn:sync-from-url"):
                    i+=1
                    self.sync_url = output[i].strip()
                i+=1


def execute(repospath=""):
    """
    Generate and return a hooks plugin object

    @param request: repos full path
    @rtype: Plugin
    @return: Plugin object
    """
    return SvnSyncMaster(repospath)

# vim: et ts=4 sw=4
