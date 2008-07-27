"""Pylons application test package

When the test runner finds and executes tests within this directory,
this file will be loaded to setup the test environment.

It registers the root directory of the project in sys.path and
pkg_resources, in case the project hasn't been installed with
setuptools. It also initializes the application via websetup (paster
setup-app) with the project's test.ini configuration file.
"""
import os
import sys
from shutil import copyfile
from unittest import TestCase

import pkg_resources
import paste.fixture
import paste.script.appinstall
from paste.deploy import loadapp
from routes import url_for

from pylons import config

__all__ = ['url_for', 'TestController']

here_dir = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.dirname(os.path.dirname(here_dir))

sys.path.insert(0, conf_dir)
pkg_resources.working_set.add_entry(conf_dir)
pkg_resources.require('Paste')
pkg_resources.require('PasteScript')

test_file = os.path.join(conf_dir, 'test.ini')
cmd = paste.script.appinstall.SetupCommand('setup-app')
cmd.run([test_file])

class TestController(TestCase):

    def __init__(self, *args, **kwargs):
        self.authz_file = os.path.dirname(__file__) + '/../../config/svn.access.test'
        wsgiapp = loadapp('config:test.ini', relative_to=conf_dir)
        self.app = paste.fixture.TestApp(wsgiapp)
        TestCase.__init__(self, *args, **kwargs)

    def rollback(self):
        src = os.path.dirname(__file__) + '/../config/svn.access.in'
        dest = self.authz_file
        copyfile(src, dest)
        
    def load_authz(self):
        from pysvnmanager.model import svnauthz
        return svnauthz.SvnAuthz(self.authz_file)
        
    def login(self, username, password=""):
        res = self.app.get(url_for(controller='security'))
        form = res.forms[0]
        form['username'] = username
        if not password:
            d = eval(config.get('test_users', {}))
            password = d.get(username,'')
        form['password'] = password
        form.submit()
