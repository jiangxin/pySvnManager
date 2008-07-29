#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pysvnmanager.tests import *
from pysvnmanager import model
from pysvnmanager.model import rcsbackup as rcs
import StringIO
import time

class TestRcsBackup(TestController):
    wcfile  = "%s/%s" % (os.path.dirname(os.path.abspath(__file__)), 'rcstest.txt')
    wcpath = os.path.dirname(os.path.abspath(wcfile))
    if os.path.isdir(wcpath+'/RCS'):
        rcsfile = wcpath+'/RCS/'+os.path.basename(wcfile)+',v'
    else:
        rcsfile = wcfile+',v'

    #def __init__(self, *args):
    #    super(TestController, self).__init__(*args)
 
    def setUp(self):
        if os.access(self.wcfile, os.R_OK):
            os.remove(self.wcfile)
        if os.access(self.rcsfile, os.R_OK):
            os.remove(self.rcsfile)

    def tearDown(self):
        if os.access(self.wcfile, os.R_OK):
            os.remove(self.wcfile)
        if os.access(self.rcsfile, os.R_OK):
            os.remove(self.rcsfile)

    def writefile(self, rev=None):
        if not rev:
            rev = self.get_revision()+1
        elif not isinstance(rev, int):
            rev = int(rev)

        f = open(self.wcfile, 'w')
        f.write('RCS working copy file\n')
        f.write('='*20 + '\n')
        f.write('Revision: %d\n' % rev)
        f.write('Date: %s\n' % time.strftime('%F %T'))
        f.close()

    def get_revision(self):
        rev = 0
        if os.access(self.wcfile, os.F_OK):
            f = open(self.wcfile, 'r')
            for line in f:
                line = line.strip()
                if line.startswith('Revision: '):
                    rev = int(line.split(':',1)[1])
                    break
        return rev

    def testBackup(self):
        # Backup test. (rcs file not exist yet)
        self.writefile()
        assert self.get_revision() == 1, self.get_revision()
        assert os.access(self.wcfile, os.R_OK)
        assert not os.access(self.rcsfile, os.R_OK)
        rcs.backup(self.wcfile)
        assert os.access(self.wcfile, os.R_OK)
        assert os.path.exists(self.rcsfile)
        assert os.access(self.rcsfile, os.R_OK), self.rcsfile

        # Backup test. (rcs exist already)
        self.writefile()
        assert os.access(self.rcsfile, os.R_OK)
        rcs.backup(self.wcfile)

        # exception test
        self.assertRaises(Exception, rcs.backup, "")

    def testRestore(self):
        rcs.restore("")
        
        # new file, backup to r1.1
        self.writefile()
        rcs.backup(self.wcfile)

        # restore from top rev: 1.1
        os.remove(self.wcfile)
        assert not os.access(self.wcfile, os.R_OK)
        rcs.restore(self.wcfile)
        assert self.get_revision() == 1, self.get_revision()

        # new file, backup to 1.2
        self.writefile()
        rcs.backup(self.wcfile)

        # backup from top rev: 1.2, and overwrite wcfile
        self.writefile()
        assert self.get_revision() == 3, self.get_revision()
        rcs.restore(self.wcfile)
        assert self.get_revision() == 2, self.get_revision()

        # backup from old rev: 1.1, and overwrite wcfile
        rcs.restore(self.wcfile, '1.1')
        assert self.get_revision() == 1, self.get_revision()

        # new file, backup to 1.3
        self.writefile(5)
        rcs.backup(self.wcfile)
        assert self.get_revision() == 5, self.get_revision()

        # restore from top rev: 1.3
        os.remove(self.wcfile)
        assert not os.access(self.wcfile, os.R_OK)
        rcs.restore(self.wcfile)
        assert self.get_revision() == 5, self.get_revision()

    def testRevision(self):
        self.writefile()
        assert os.access(self.wcfile, os.R_OK)
        pass

    def testLogs(self):
        self.writefile()
        assert os.access(self.wcfile, os.R_OK)
        print "testLogs"
        pass

if __name__ == '__main__': 
    import unittest
    unittest.main()

