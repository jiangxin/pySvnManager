# -*- coding: utf-8 -*-

import ConfigParser
import os
import time
import logging

# i18n works only as pysvnmanager (a pylons app) model.
from pylons import config
if config.get('package') and not config.has_key('unittest'):
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
    # Brief name for this plugin.
    name = ""
    
    # Longer description for this plugin.
    description = ""

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

    def get_config(self, key, default="", section='main'):
        """
        Get config from the default config file.
        """
        if not self.cp.has_section(section):
            self.cp.add_section(section)
        if self.cp.has_option(section, key):
            result = self.cp.get(section, key)
        else:
            result = default
        return result

    def has_config(self):
        """
        Test if self.key = self.value is in the default config ini file.
        """
        if not hasattr(self, "key") or not hasattr(self, "value"):
            raise Exception, _("Plugin not fully implemented.")
        
        if hasattr(self, "section"):
            section = self.section
        else:
            section = 'main'
        
        return self.get_config(self.key, section=section) == self.value
        
    def set_config(self):
        """
        add self.key = self.value to default config ini file.
        """
        if not hasattr(self, "key") or not hasattr(self, "value"):
            raise Exception, _("Plugin not fully implemented.")
        
        if hasattr(self, "section"):
            section = self.section
        else:
            section = 'main'
            
        if not self.cp.has_section(section):
            self.cp.add_section(section)
        self.cp.set(section, self.key, self.value)

    def unset_config(self):
        """
        Remove self.key from default config ini file.
        """
        if not hasattr(self, "key") or not hasattr(self, "value"):
            raise Exception, _("Plugin not fully implemented.")
        
        if hasattr(self, "section"):
            section = self.section
        else:
            section = 'main'
        
        if self.cp.has_section(section):
            self.cp.remove_option(section, self.key)
            # test if section is blank after remove option.
            if not self.cp.options(section):
                self.cp.remove_section(section)
    
    def get_detail(self):
        """
        Show detail informantion if plugin is already installed.
        """
        if self.enabled():
            return self.description
        else:
            return ""
    
    detail = property(get_detail)
    
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
        
        Default: just output description.
        """
        result = "<ul><li>" + _("Plugin name") + ": " + self.name + "\n" + \
                 "<li>" + _("Type") + ": " + self.get_type() + "\n" + \
                 "<li>" + _("Description") + ": " + self.description + "\n"
        return result

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
