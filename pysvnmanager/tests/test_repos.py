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

import os
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pysvnmanager.lib.base import *
from pysvnmanager.tests import *
from pysvnmanager import model
from pysvnmanager.model import repos
from pysvnmanager.model import hooks
from pysvnmanager.hooks import plugins

import pylons.test

import StringIO
from pprint import pprint

class TestRepos(TestController):
    
    def __init__(self, *args):
        # self.repos_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/svnroot.test'
        wsgiapp = pylons.test.pylonsapp
        config = wsgiapp.config
        self.repos_root = config.get('repos_root', "") % {'here': config.get('here')}
        self.repos = repos.Repos(self.repos_root)
        super(TestRepos, self).__init__(*args)

    def setUp(self):
        #print '+'*40, 'setup'
        pass

    def tearDown(self):
        #print '+'*40, 'teardown'
        pass
    
    def testReposCreate(self):
        self.assertRaises(Exception, self.repos.create, 'repos3')
        try:
            self.repos.delete('repos3')
            self.repos.create('repos3')
            self.assert_(sorted(self.repos.repos_list) == [u'project1', u'project2', u'repos3'], self.repos.repos_list)
        except ImportError:
            pass

    def testReposDelete(self):
        try:
            self.repos.delete('project1')
        except Exception, e:
            self.assert_(str(e) == 'Repos project1 is not a blank repository.', str(e))
    
    def testReposRoot(self):
        repos.Repos('/tmp')
        self.assertRaises(Exception, repos.Repos, '/tmp/svnroot.noexists')

    def testReposlist(self):
        self.assert_(sorted(self.repos.repos_list) == ['project1', 'project2', 'repos3'], u','.join(self.repos.repos_list).encode('utf-8'))

    def testSvnVersion(self):
        svnversion = self.repos.svnversion()
        self.assert_(svnversion[0]!='', svnversion[0])
        self.assert_(svnversion[1]!='', svnversion[1])

class TestReposPlugin(TestController):
    
    def __init__(self, *args):
        # self.repos_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/svnroot.test'
        wsgiapp = pylons.test.pylonsapp
        config = wsgiapp.config
        self.repos_root = config.get('repos_root', "") % {'here': config.get('here')}
        super(TestReposPlugin, self).__init__(*args)

    def setUp(self):
        #print '+'*40, 'setup'
        pass

    def tearDown(self):
        #print '+'*40, 'teardown'
        pass

    def testPluginList(self):
        self.assert_('CaseInsensitive' in plugins.modules, plugins.modules)
        self.assert_('EolStyleCheck' in plugins.modules, plugins.modules)
      
    def testPluginImport(self):
        self.assertRaises(Exception,  plugins.getHandler("CaseInsensitive"), "")
        module_ci = plugins.getHandler("CaseInsensitive")(self.repos_root + '/project1')
        self.assert_(module_ci.name=="Detect case-insensitive filename clashes", module_ci.name)
        self.assert_(module_ci.description!="", module_ci.description)
      
    def testPluginSetting(self):
        m = plugins.getHandler("CaseInsensitive")(self.repos_root + '/project1')
        self.assert_(m.enabled()==False)
        m.install()
        self.assert_(m.enabled()==True)
        m.uninstall()
        self.assert_(m.enabled()==False)
      
    def testHooks(self):
        # self.repos_root is not a repository.
        self.assertRaises(AssertionError, hooks.Hooks, self.repos_root)
        
        myhooks = hooks.Hooks(self.repos_root + '/project1')
        self.assert_('CaseInsensitive' in myhooks.pluginnames, myhooks.pluginnames)
        self.assert_('EolStyleCheck' in myhooks.pluginnames, myhooks.pluginnames)
        
        self.assert_('CaseInsensitive' in myhooks.unapplied_plugins, myhooks.unapplied_plugins)
        self.assert_('EolStyleCheck' in myhooks.unapplied_plugins, myhooks.unapplied_plugins)
        
        m = myhooks.plugins['CaseInsensitive']
        self.assert_(m.name=="Detect case-insensitive filename clashes", m.name)
        self.assert_(m.description!="", m.description)
    
    def testHooksSetting(self):
        myhooks = hooks.Hooks(self.repos_root + '/project1')

        m = myhooks.plugins['CaseInsensitive']
        self.assert_(m.enabled()==False)
        self.assert_('CaseInsensitive' not in myhooks.applied_plugins, myhooks.applied_plugins)
        self.assert_('EolStyleCheck' not in myhooks.applied_plugins, myhooks.applied_plugins)
        self.assert_('CaseInsensitive' in myhooks.unapplied_plugins, myhooks.unapplied_plugins)
        self.assert_('EolStyleCheck' in myhooks.unapplied_plugins, myhooks.unapplied_plugins)

        m.install()
        self.assert_(m.enabled()==True)
        self.assert_('CaseInsensitive' in myhooks.applied_plugins, myhooks.applied_plugins)
        self.assert_('EolStyleCheck' not in myhooks.applied_plugins, myhooks.applied_plugins)
        self.assert_('CaseInsensitive' not in myhooks.unapplied_plugins, myhooks.unapplied_plugins)
        self.assert_('EolStyleCheck' in myhooks.unapplied_plugins, myhooks.unapplied_plugins)

        m.uninstall()
        self.assert_(m.enabled()==False)
        self.assert_('CaseInsensitive' not in myhooks.applied_plugins, myhooks.applied_plugins)
        self.assert_('EolStyleCheck' not in myhooks.applied_plugins, myhooks.applied_plugins)
        self.assert_('CaseInsensitive' in myhooks.unapplied_plugins, myhooks.unapplied_plugins)
        self.assert_('EolStyleCheck' in myhooks.unapplied_plugins, myhooks.unapplied_plugins)


if __name__ == '__main__': 
    import unittest
    unittest.main()
