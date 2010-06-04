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

import ConfigParser
import os
import time
import logging

from pysvnmanager.model.rest import reSTify

# i18n works only as pysvnmanager (a pylons app) model.
from pylons import config
if not config.has_key('unittest'):
    from pylons.i18n import _
else:
    _ = lambda x:x
    
log = logging.getLogger(__name__)

def getPackageModules(packagefile):
    """
    Return a list of modules for a package, omitting any modules
    starting with an underscore.
    """
    import os, re
    
    packagedir = os.path.dirname(packagefile)
    pyre = re.compile(r"^([^_].*)\.py$")
    dirlist = os.listdir(packagedir)

    matches = [pyre.match(fn) for fn in dirlist]
    modules = [match.group(1) for match in matches if match]

    modules.sort()
    return modules


def getHandler(name, function="execute"):
    """ return a handler function for a given action or None """
    if function:
        fromlist = [function]
    else:
        fromlist = []
    moduleName = 'pysvnmanager.hooks.plugins.' + name
    module = __import__(moduleName, globals(), {}, fromlist)

    if function:
        # module has the obj for module <moduleName>
        return getattr(module, function)
    else:
        # module now has the toplevel module of <moduleName> (see __import__ docs!)
        components = moduleName.split('.')
        for comp in components[1:]:
            module = getattr(module, comp)
        return module

T_START_COMMIT          = 1
T_PRE_COMMIT            = 2
T_POST_COMMIT           = 3
T_PRE_REVPROP_CHANGE    = 4
T_POST_REVPROP_CHANGE   = 5
T_PRE_LOCK              = 6
T_POST_LOCK             = 7
T_PRE_UNLOCK            = 8
T_POST_UNLOCK           = 9

class PluginBase(object):
    """ Base class for hook plugins
    """
    # Plugin id (will be set automatically after instance initialized)
    id = None # __name__.rsplit('.',1)[-1]

    # Both description and detail are reStructuredText format. 
    # Reference about reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html
    
    # Brief name for this plugin.
    name = ""
    
    # Short description for this plugin.
    description = ""

    # Long description for this plugin.
    detail = ""

    # Hooks-plugin type: T_START_COMMIT, ..., T_POST_UNLOCK
    type = 0
    
    # Store file timestamp as plugin revision, avoid config confliction.
    # Not edit it manually.
    revision = ""
    
    def __init__(self, repospath):
        # Test if repository is exists.
        self.__repospath = repospath
        if not os.path.exists(self.__repospath):
            raise Exception, _("repos '%s' not exist!") % os.path.basename(self.__repospath)

        # Read configuration from the default config ini file.
        self.__configfile = "%s/conf/hooks.ini" % self.__repospath
        self.__read_config()

    def __read_config(self, force=False):
        # only read config file if out-of-date.
        if force or self.__is_outofdate():
            #log.debug("config is outofdate for '%s'." % self.name)
            timestamp = os.path.getmtime(self.__configfile)

            # ConfigParser has not cleanup method, so we initial it again.
            self.cp = ConfigParser.ConfigParser()
            self.cp.read(self.__configfile)

            # Set timestamp as revision
            self.revision = timestamp            
        # if config file not exist.
        elif not self.revision:
            self.cp = ConfigParser.ConfigParser()
            self.cp.add_section('main')
            self.revision = time.time()
    
    def __is_outofdate(self):
        """
        Test if timestamp of the config file is the same we load it last time.
        """
        if os.path.exists(self.__configfile):
            timestamp = os.path.getmtime(self.__configfile)
            if not self.revision or self.revision != timestamp:
                return True
        # not out-of-date if config file not exist, or timestamp not changed.
        return False
    
    def __cmp__(self, obj):
        assert isinstance(obj, PluginBase)
        if self.type == obj.type:
            return cmp(self.id, obj.id)
        else:
            return cmp(self.type, obj.type)
        
        
    def reload(self, force=True):
        """
        Reload the default config ini file, if out-of-date.
        """
        self.__read_config(force)
    
    def save(self):
        """
        Save config to the default config ini file.
        
        If the file modified time is different with the time last load, Conflict raises.
        """
        # Test if timestamp of the config file is the same we load it last time.
        if self.__is_outofdate():
            raise Exception(_("Conflict: plugin '%s' is modified by others.") % self.name)
        
        # Save to file.
        fp = open(self.__configfile, 'w')
        self.cp.write(fp)
        fp.close()
        
        # Update revision as file timestamp.
        self.revision = os.path.getmtime(self.__configfile)

    def get_config(self, key, default="", section=''):
        """
        Get config from the default config file.
        """
        if not section:
            section = self.section
        if not self.cp.has_section(section):
            self.cp.add_section(section)
        if self.cp.has_option(section, key):
            result = self.cp.get(section, key)
        else:
            result = default
        return result

    def has_config(self, key="", value=""):
        """
        Test if self.key = self.value is in the default config ini file.
        """
        if key == "":
            if not hasattr(self, "key"):
                raise Exception, _("Plugin not fully implemented.")
            else:
                key = self.key

        if value == "" and hasattr(self, "value"):
            value = self.value
        
        if hasattr(self, "section"):
            section = self.section
        else:
            section = 'main'
        
        setting = self.get_config(key, section=section)
        if value:
            return setting == value
        elif setting != "":
            return True
        else:
            return False
        
    def set_config(self, key="", value=""):
        """
        add self.key = self.value to default config ini file.
        """
        if key == "":
            if not hasattr(self, "key"):
                raise Exception, _("Plugin not fully implemented.")
            else:
                key = self.key

        if value == "" and hasattr(self, "value"):
            value = self.value
        
        if hasattr(self, "section"):
            section = self.section
        else:
            section = 'main'
            
        if not self.cp.has_section(section):
            self.cp.add_section(section)
        self.cp.set(section, key, value)

    def unset_config(self, key=""):
        """
        Remove self.key from default config ini file.
        """
        if key == "":
            if not hasattr(self, "key"):
                raise Exception, _("Plugin not fully implemented.")
            else:
                key = self.key
        
        if hasattr(self, "section"):
            section = self.section
        else:
            section = 'main'
        
        if self.cp.has_section(section):
            self.cp.remove_option(section, key)
            # test if section is blank after remove option.
            if not self.cp.options(section):
                self.cp.remove_section(section)
    
    def install_info(self):
        """
        Show configurations if plugin is already installed.
        
        return reStructuredText.
        reST reference: http://docutils.sourceforge.net/docs/user/rst/quickref.html
        """
        return self.description
    
    def show_install_info(self):
        return reSTify(self.install_info())
    
    def get_type(self):
        type = "UNDEFINED"
        if self.type == T_START_COMMIT:
            type = "start-commit"
        elif self.type == T_PRE_COMMIT:
            type = "pre-commit"
        elif self.type == T_POST_COMMIT:
            type = "post-commit"
        elif self.type == T_PRE_REVPROP_CHANGE:
            type = "pre-revprop-change"
        elif self.type == T_POST_REVPROP_CHANGE:
            type = "post-revprop-change"
        elif self.type == T_PRE_LOCK:
            type = "pre-lock"
        elif self.type == T_POST_LOCK:
            type = "post-lock"
        elif self.type == T_PRE_UNLOCK:
            type = "pre-unlock"
        elif self.type == T_POST_UNLOCK:
            type = "post-unlock"
        return type

    def install_config_form(self):
        """
        This method will be called to build setup configuration form.
        If this plugin needs parameters, provides form fields here.
        Any html and javascript are welcome.
        
        If plugin does not need further configuration, simply return null str.
        """
        return ""
        
    def show_install_config_form(self):
        """
        This method will be called to build setup configuration form.
        If this plugin needs parameters, provides form fields here.
        Any html and javascript are welcome.
        
        return output reSTified html.
        """
        header = """
**%(id)s**

- %(t_name)s: %(name)s
- %(t_type)s: %(type)s

**%(t_desc)s**

%(desc)s

%(detail)s
""" % {
                't_name': _('Name'),
                't_type': _('Type'),
                't_desc': _('Description'),
                'id':self.id.rsplit('.',1)[-1],
                'name': self.name,
                'type': self.get_type(),
                'desc': self.description,
                'detail': self.detail,
                }

        header = reSTify(header)
        form = self.install_config_form() or ""
        return header + form
        
    def enabled(self):
        """
        Return True, if this plugin has been setup.
        Simply call 'has_config()'.
        """
        raise Exception, _("Plugin not fully implemented.")
            
    def uninstall(self):
        """
        Uninstall hooks-plugin from repository.
        Simply call 'unset_config()' and 'save()'.
        """
        raise Exception, _("Plugin not fully implemented.")
    
    def install(self, params=None):
        """
        Install hooks-plugin from repository.
        Simply call 'set_config()' and 'save()'.
        
        Form fields in setup_config() will pass as params.
        """
        raise Exception, _("Plugin not fully implemented.")
    
    
modules = getPackageModules(__file__)
