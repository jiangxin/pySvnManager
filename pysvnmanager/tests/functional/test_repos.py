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

class TestReposController(TestController):

    def test_index(self):

        # Test redirect to login pange
        res = self.app.get(url_for(controller='repos'))
        assert res.status == 302
        self.assertEqual(res.header('location'), 'http://localhost/login')

        # Login as common user
        self.login('nobody')
        res = self.app.get(url_for(controller='repos'))
        assert res.status == 302, res.status
        assert res.header('location')=='http://localhost/security/failed', res.header('location')
        
        # Permission denied for repos admin(not root admin)
        self.login('admin2')
        res = self.app.get(url_for(controller='repos'))
        assert res.status == 302, res.status
        assert res.header('location')=='http://localhost/security/failed', res.header('location')

        # Login as superuser
        self.login('root')
        res = self.app.get(url_for(controller='repos'))
        assert res.status == 200
        assert """<div id="installed_hook_form_contents"></div>""" in res.body, res.body[:100]

    def test_init_repos_list(self):
        # Login as superuser
        self.login('root')
        res = self.app.get(url_for(controller='repos', action="init_repos_list"))
        assert res.status == 200
        assert """id[0]="...";name[0]="Please choose...";
id[1]="project1";name[1]="project1";
id[2]="project2";name[2]="project2";
id[3]="repos3";name[3]="repos3";
total=4;
""" in res.body, res.body[:100]
    
    def test_get_plugin_list(self):
        self.login('root')
        params = {
                  'select':'project1', 
                  }
        res = self.app.get(url_for(controller='repos', action="get_plugin_list"), params)
        assert res.status == 200
        assert "CaseInsensitive" in res.body, res.body
        assert "EolStyleCheck" in res.body, res.body
        assert "Please choose..." in res.body, res.body
    
    def test_get_installed_hook_form(self):
        self.login('root')
        params = {
                  'select':'project1', 
                  }
        res = self.app.get(url_for(controller='repos', action="get_installed_hook_form"), params)
        assert res.status == 200
        assert "" == res.body, res.body

    def test_get_hook_setting_form(self):
        self.login('root')
        params = {
                  'repos':'project1', 
                  'plugin':'CaseInsensitive',
                  }
        res = self.app.get(url_for(controller='repos', action="get_hook_setting_form"), params)
        assert res.status == 200
        assert "A pre-commit hook to detect case-insensitive filename clashes." in res.body, res.body
    
    def test_install_uninstall_hook(self):
        self.login('root')
        params = {
                  '_repos':'project1',
                  '_plugin':'CaseInsensitiveXXX',
                  }
        res = self.app.get(url_for(controller='repos', action="setup_hook"), params)
        assert res.status == 200
        assert "Apply plugin 'CaseInsensitiveXXX' on 'project1' Failed" in res.body, res.body

        self.login('root')
        params = {
                  'select':'project1', 
                  }
        res = self.app.get(url_for(controller='repos', action="get_plugin_list"), params)
        assert res.status == 200
        assert "CaseInsensitive" in res.body, res.body
        assert "EolStyleCheck" in res.body, res.body
        assert "Please choose..." in res.body, res.body

        self.login('root')
        params = {
                  '_repos':'project1',
                  '_plugin':'CaseInsensitive',
                  }
        res = self.app.get(url_for(controller='repos', action="setup_hook"), params)
        assert res.status == 200
        assert "<div class='info'>Apply plugin 'CaseInsensitive' on 'project1' success.</div>" == res.body, res.body

        self.login('root')
        params = {
                  'select':'project1', 
                  }
        res = self.app.get(url_for(controller='repos', action="get_plugin_list"), params)
        assert res.status == 200
        assert "CaseInsensitive" not in res.body, res.body
        assert "EolStyleCheck" in res.body, res.body
        assert "Please choose..." in res.body, res.body

        self.login('root')
        params = {
                  '_repos':'project1',
                  '_plugin':'EolStyleCheck',
                  }
        res = self.app.get(url_for(controller='repos', action="setup_hook"), params)
        assert res.status == 200
        assert """<div class='info'>Apply plugin 'EolStyleCheck' on 'project1' success.</div>""" == res.body, res.body

        self.login('root')
        params = {
                  'select':'project1', 
                  }
        res = self.app.get(url_for(controller='repos', action="get_plugin_list"), params)
        assert res.status == 200
        assert "CaseInsensitive" not in res.body, res.body
        assert "EolStyleCheck" not in res.body, res.body
        assert "Please choose..." in res.body, res.body

        self.login('root')
        params = {
                  '_repos':'project1',
                  'pluginid_0':'CaseInsensitive',
                  'pluginid_1':'EolStyleCheck',
                  }
        res = self.app.get(url_for(controller='repos', action="uninstall_hook"), params)
        assert res.status == 200
        assert """<div class='info'>Delete plugin 'CaseInsensitive, EolStyleCheck' on 'project1' success.</div>""" == res.body, res.body

        self.login('root')
        params = {
                  'select':'project1', 
                  }
        res = self.app.get(url_for(controller='repos', action="get_plugin_list"), params)
        assert res.status == 200
        assert "CaseInsensitive" in res.body, res.body
        assert "EolStyleCheck" in res.body, res.body
        assert "Please choose..." in res.body, res.body

        
    