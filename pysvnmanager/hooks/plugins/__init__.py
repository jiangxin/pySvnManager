# create a list of extension actions from the package directory
import ConfigParser
import os

def getPackageModules(packagefile):
    """ Return a list of modules for a package, omitting any modules
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


class PluginBase(object):
    """ Base class for hook plugins
    """
    name = ""
    description = ""
    
    def __init__(self, repospath):
        self.__repospath = repospath
        if not os.path.exists(self.__repospath):
            raise Exception, "repos '%s' not exist!" % os.path.basename(self.__repospath)
        self.__configfile = "%s/conf/hooks.ini" % self.__repospath
        self.cp = ConfigParser.ConfigParser()
        self.__read_config()

    def __read_config(self):
        if os.path.exists(self.__configfile):
            self.cp.read(self.__configfile)
        else:
            self.cp.add_section('main')
    
    def write(self):
        fp = open(self.__configfile, 'w')
        self.cp.write(fp)

    def get_config(self, option, default="", section='main'):
        if not self.cp.has_section(section):
            self.cp.add_section(section)
        if self.cp.has_option(section, option):
            result = self.cp.get(section, option)
        else:
            result = default
        return result

    def set_config(self, option, value="", section='main'):
        if not self.cp.has_section(section):
            self.cp.add_section(section)
        self.cp.set(section, option, value)

    def del_config(self, option, section='main'):
        if self.cp.has_section(section):
            self.cp.remove_option(section, option)
            if not self.cp.options(section):
                self.cp.remove_section(section)

    def is_set(self):
        raise Exception, "Not implement."
    
    def show(self):
        return self.description
    
    def show_form(self):
        return self.description
            
    def delete_plugin(self):
        raise Exception, "Not implement."
    
    def set_plugin(self, form=None):
        raise Exception, "Not implement."
    
    
modules = getPackageModules(__file__)
