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
from unittest import TestCase

from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from pylons import url
from routes.util import URLGenerator
from webtest import TestApp

import pylons.test

__all__ = ['environ', 'url', 'TestController']

# Invoke websetup with the current config file
SetupCommand('setup-app').run([pylons.test.pylonsapp.config['__file__']])

environ = {}

import os
import sys
from shutil import copyfile

class TestController(TestCase):

    def __init__(self, *args, **kwargs):
        self.authz_file = os.path.dirname(__file__) + '/../../config/svn.access.test'

        wsgiapp = pylons.test.pylonsapp
        config = wsgiapp.config
        self.app = TestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))
        TestCase.__init__(self, *args, **kwargs)

    def rollback(self):
        src = os.path.dirname(__file__) + '/../config/svn.access.example'
        dest = self.authz_file
        copyfile(src, dest)
        
    def load_authz(self):
        from pysvnmanager.model import svnauthz
        return svnauthz.SvnAuthz(self.authz_file)
        
    def login(self, username, password=""):
       
        if not password:
            wsgiapp = pylons.test.pylonsapp
            config = wsgiapp.config
            d = eval(config.get('test_users', {}))
            password = d.get(username,'')

        r = self.app.post(url(controller='security', action='submit'), params={'username': username, 'password': password})

        #res = self.app.get(url(controller='security', action='index'))
        #form = res.forms[0]
        #form['username'] = username
        #if not password:
        #    wsgiapp = pylons.test.pylonsapp
        #    config = wsgiapp.config
        #    d = eval(config.get('test_users', {}))
        #    password = d.get(username,'')
        #form['password'] = password
        #form.submit()
