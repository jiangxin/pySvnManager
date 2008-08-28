#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Subversion repos management.

Basic classes used for Subversion repository add/remove.
"""

import re
import sys
import os
import StringIO
import logging
log = logging.getLogger(__name__)

from pylons import config
config_path = config["here"] + '/config'
if config_path not in sys.path:
    sys.path.insert(0, config_path)
from localconfig import LocalConfig as cfg

sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from pysvnmanager import hooks

# i18n works only as pysvnmanager (a pylons app) model.
if config.get('package') and not config.has_key('unittest'):
    from pylons.i18n import _
else:
    def _(message): return message

#reload(sys) # in Python2.5, method sys.setdefaultencoding 
            #will be delete after initialize. we need reload it.
#sys.setdefaultencoding('utf-8')

class Repos:
    
    def __init__(self, repos_root):
        if not repos_root or not os.path.exists(repos_root):
            raise Exception, _("Repos root does not exist: %s") % repos_root
        
        self.__repos_root = os.path.abspath(repos_root)
        self.__repos_list = []
        self.svnversion_re = re.compile(ur'version\s+(?P<main>[\S]+)(\s+\((?P<sub>.*)\))?')
    
    def __get_repos_root(self):
        return self.__repos_root
    
    repos_root = property(__get_repos_root)
    
    def __get_repos_list(self):
        self.__repos_list = []
        for i in os.listdir(self.repos_root):
            i=unicode(i, 'utf-8')
            if self.is_svn_repos(i):
                self.__repos_list.append(i)

        self.__repos_list = sorted(self.__repos_list)
        return self.__repos_list

    repos_list = property(__get_repos_list)
        
    def create(self, repos_name):
        repos_name = repos_name.strip()
        assert repos_name != ""

        repos_path = "%(root)s/%(entry)s" % { "root": self.repos_root, "entry": repos_name}
        if os.path.exists(repos_path):
            raise Exception, _("Repos %s already exists.") % repos_name
        from svn import repos as _repos
        if isinstance(repos_path, unicode):
            repos_path = repos_path.encode('utf-8')
        _repos.create(repos_path, "", "", None, { "fs-type": "fsfs" })
        self.hooks_init(repos_name)
    
    def hooks_init(self, repos_name):
        import distutils.version as dv
        version = '.'.join(self.svnversion())
        matched = 'default'
        for ver in sorted(hooks.init.svn_hooks_init_dict.keys(),
                          cmp = lambda x,y: cmp(dv.LooseVersion(x), dv.LooseVersion(y)),
                          reverse=True):
            if dv.LooseVersion(version) >= dv.LooseVersion(ver):
                matched = ver
                break
        
        #log.debug('Hooks version matched: %s' % matched)
        #log.debug('svn_hooks_init_base: %s' % hooks.init.svn_hooks_init_base)
        
        # copy hook-scripts from matched hooks templates directory.
        src = hooks.init.svn_hooks_init_base + '/' + hooks.init.svn_hooks_init_dict[matched]
        dest = "%(root)s/%(entry)s/hooks" % { "root": self.repos_root, "entry": repos_name}
        
        log.debug('Now copy hooks from \n\t%s to \n\t%s' % (src, dest))
        import shutil
        shutil.rmtree(dest)
        shutil.copytree(src, dest, symlinks=True)
        
    
    def svnversion(self):
        cmd = 'LC_ALL=C svn --version'
        buff = os.popen(cmd).readline().strip()
        m = self.svnversion_re.search(buff)
        if m:
            return (m.group('main'), m.group('sub'))
        else:
            return (None, None)
    
    def is_svn_repos(self, repos_name):
        repos_path = "%(root)s/%(entry)s" % { "root": self.repos_root, "entry": repos_name}
        if os.path.exists(repos_path):
            if os.path.exists("%s/db/revs/0" % repos_path) and \
                os.path.exists("%s/hooks" % repos_path):
                return True
        log.info("'%(entry)s' is not svn repository below %(root)s" % { "root": self.repos_root, "entry": repos_name} )
        return False
    
    def is_blank_svn_repos(self, repos_name):
        if self.is_svn_repos(repos_name):
            repos_path = "%(root)s/%(entry)s" % { "root": self.repos_root, "entry": repos_name}
            if len(os.listdir("%s/db/revs" % repos_path))!= 1:
                return False
            elif os.path.isdir("%s/db/revs/0" % repos_path) and \
                len(os.listdir("%s/db/revs/0" % repos_path))!= 1:
                return False
            else:
                return True

        return False
            
    def delete(self, repos_name):
        repos_name = repos_name.strip()
        assert repos_name != ""
        repos_path = "%(root)s/%(entry)s" % { "root": self.repos_root, "entry": repos_name}
        if os.path.exists(repos_path):
            if self.is_blank_svn_repos(repos_name):
                from svn import repos as _repos
                return _repos.delete(repos_path)
        
        raise Exception, _("Repos %s is not a blank repository.") % repos_name
        
        

if __name__ == '__main__':
    import doctest
    doctest.testmod()
