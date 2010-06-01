## -*- coding: utf-8 -*-
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

from pysvnmanager.tests import *
import pylons.test

class TestLoginController(TestController):

    def test_login_logout(self):
        wsgiapp = pylons.test.pylonsapp
        config = wsgiapp.config
        params={}
        # login successful
        params['username'] = 'root'
        d = eval(config.get('test_users', {}))
        password = d.get(params['username'],'')
        params['password'] = password
        res = self.app.get(url(controller='security', action='submit'), params)
        self.assert_(res.status == "302 Found", res.status)
        self.assert_(res.location == '/' or res.location == 'http://localhost/', res.location)
        self.assert_(res.session['user'] == 'root', res.session)
        
        # keep session test
        res = self.app.get(url(controller='security', action='index'))
        self.assert_('<h2>Login</h2>' in res.body, res.body)
        self.assert_(res.session['user'] == 'root', res.session)
                                   
        # login with wrong password
        params['username'] = 'root'
        params['password'] = 'wrong_passwd'
        res = self.app.get(url(controller='security', action='submit'), params)
        self.assert_(res.status == "200 OK", res.status)
        self.assert_('Login failed for user: root' in res.body, res.body)
        self.assert_(res.session.get('user') == None, res.session.get('user'))
        
        self.login('jiangxin')
        res = self.app.get(url(controller='security', action='index'))
        self.assert_(res.session.get('user') == 'jiangxin', res.session)

        # logout
        res = self.app.get(url(controller='security', action='logout'))
        self.assert_(res.status == "302 Found", res.status)
        self.assert_(res.location == '/login' or res.location == 'http://localhost/login', res.location)
        self.assert_(res.session.get('user') == None, res.session.get('user'))
