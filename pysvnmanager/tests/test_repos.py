#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pysvnmanager.tests import *
from pysvnmanager import model
from pysvnmanager.model import repos
import StringIO
from pprint import pprint

class TestRepos(TestController):
    
    def __init__(self, *args):
        repos_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/svnroot'
        self.repos = repos.Repos(repos_root)
        super(TestRepos, self).__init__(*args)

    def setUp(self):
        #print '+'*40, 'setup'
        pass

    def tearDown(self):
        #print '+'*40, 'teardown'
        pass
    
    def testReposRoot(self):
        repos.Repos('/tmp')
        self.assertRaises(Exception, repos.Repos, '/tmp/svnroot.noexists')

    def testReposlist(self):
        self.assert_(sorted(self.repos.repos_list) == ['repos1', 'repos2'], u','.join(self.repos.repos_list).encode('utf-8'))

    def testReposCreate(self):
        self.assertRaises(Exception, self.repos.create, 'repos1')
        self.repos.create('repos3')
        self.assert_(sorted(self.repos.repos_list) == ['repos1', 'repos2', 'repos3'], self.repos.repos_list)
        self.repos.delete('repos3')

    def testReposDelete(self):
        self.assertRaises(Exception, self.repos.delete, 'repos1')
    
    def testSvnVersion(self):
        svnversion = self.repos.svnversion()
        self.assert_(svnversion[0]!='', svnversion[0])
        self.assert_(svnversion[1]!='', svnversion[1])
    
if __name__ == '__main__': 
    import unittest
    unittest.main()
