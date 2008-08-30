# -*- coding: utf-8 -*-
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

"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
import os
import sys
from shutil import copyfile
from pylons import config

from unittest import TestCase

from paste.deploy import loadapp
from paste.fixture import TestApp
from paste.script.appinstall import SetupCommand
from pylons import config
from routes import url_for

import pylons.test
import pkg_resources

__all__ = ['url_for', 'TestController']

here_dir = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.dirname(os.path.dirname(here_dir))

sys.path.insert(0, conf_dir)
pkg_resources.working_set.add_entry(conf_dir)
pkg_resources.require('Paste')
pkg_resources.require('PasteScript')

test_file = os.path.join(conf_dir, 'test.ini')

# Invoke websetup with the current config file
SetupCommand('setup-app').run([config['__file__']])

class TestController(TestCase):

    def __init__(self, *args, **kwargs):
        self.authz_file = os.path.dirname(__file__) + '/../../config/svn.access.test'
        if pylons.test.pylonsapp:
            wsgiapp = pylons.test.pylonsapp
        else:
            wsgiapp = loadapp('config:%s' % config['__file__'])
        self.app = TestApp(wsgiapp)
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
