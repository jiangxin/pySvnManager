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
        res = self.app.get(url(controller='repos', action='index'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/login'), res.location

        # Login as common user
        self.login('nobody')
        res = self.app.get(url(controller='repos', action='index'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/security/failed'), res.location
        
        # repos admin can access repos controller(not root admin), but only with authed repos
        self.login('admin2')
        res = self.app.get(url(controller='repos', action='index'))
        assert res.status == "200 OK", res.status

        # ??? Repos admin can or can not manage hooks for his/her repos ???
        self.login('admin2')
        res = self.app.get(url(controller='repos', action='init_repos_list'))
        assert """id[0]="...";name[0]="Please choose...";
total=1;""" in res.body, res.body

        # Login as superuser
        self.login('root')
        res = self.app.get(url(controller='repos', action='index'))
        assert res.status == "200 OK", res.status
        assert """<div id="installed_hook_form_contents"></div>""" in res.body, res.body[:100]

    def test_init_repos_list(self):
        # Login as superuser
        self.login('root')
        res = self.app.get(url(controller='repos', action="init_repos_list"))
        assert res.status == "200 OK", res.status
        assert """id[0]="...";name[0]="Please choose...";
id[1]="repos3";name[1]="repos3";
id[2]="project1";name[2]="project1 (!)";
id[3]="project2";name[3]="project2 (!)";
total=4;""" in res.body, res.body[:"200 OK"]
    
    def test_get_plugin_list(self):
        self.login('root')
        params = {
                  'select':'project1', 
                  }
        res = self.app.get(url(controller='repos', action="get_plugin_list"), params)
        assert res.status == "200 OK", res.status
        assert "CaseInsensitive" in res.body, res.body
        assert "EolStyleCheck" in res.body, res.body
        assert "Please choose..." in res.body, res.body
    
    def test_get_installed_hook_form(self):
        self.login('root')
        params = {
                  'select':'project1', 
                  }
        res = self.app.get(url(controller='repos', action="get_installed_hook_form"), params)
        assert res.status == "200 OK", res.status
        assert "" == res.body, res.body

    def test_get_hook_setting_form(self):
        self.login('root')
        params = {
                  'repos':'project1', 
                  'plugin':'CaseInsensitive',
                  }
        res = self.app.get(url(controller='repos', action="get_hook_setting_form"), params)
        assert res.status == "200 OK", res.status
        assert "A pre-commit hook to detect case-insensitive filename clashes." in res.body, res.body
    
    def test_install_uninstall_hook(self):
        self.login('root')
        params = {
                  '_repos':'project1',
                  '_plugin':'CaseInsensitiveXXX',
                  }
        res = self.app.get(url(controller='repos', action="setup_hook"), params)
        assert res.status == "200 OK", res.status
        assert "Apply plugin 'CaseInsensitiveXXX' on 'project1' Failed" in res.body, res.body

        self.login('root')
        params = {
                  'select':'project1', 
                  }
        res = self.app.get(url(controller='repos', action="get_plugin_list"), params)
        assert res.status == "200 OK", res.status
        assert "CaseInsensitive" in res.body, res.body
        assert "EolStyleCheck" in res.body, res.body
        assert "Please choose..." in res.body, res.body

        self.login('root')
        params = {
                  '_repos':'project1',
                  '_plugin':'CaseInsensitive',
                  }
        res = self.app.get(url(controller='repos', action="setup_hook"), params)
        assert res.status == "200 OK", res.status
        assert "<div class='info'>Apply plugin 'CaseInsensitive' on 'project1' success.</div>" == res.body, res.body

        self.login('root')
        params = {
                  'select':'project1', 
                  }
        res = self.app.get(url(controller='repos', action="get_plugin_list"), params)
        assert res.status == "200 OK", res.status
        assert "CaseInsensitive" not in res.body, res.body
        assert "EolStyleCheck" in res.body, res.body
        assert "Please choose..." in res.body, res.body

        self.login('root')
        params = {
                  '_repos':'project1',
                  '_plugin':'EolStyleCheck',
                  }
        res = self.app.get(url(controller='repos', action="setup_hook"), params)
        assert res.status == "200 OK", res.status
        assert """<div class='info'>Apply plugin 'EolStyleCheck' on 'project1' success.</div>""" == res.body, res.body

        self.login('root')
        params = {
                  'select':'project1', 
                  }
        res = self.app.get(url(controller='repos', action="get_plugin_list"), params)
        assert res.status == "200 OK", res.status
        assert "CaseInsensitive" not in res.body, res.body
        assert "EolStyleCheck" not in res.body, res.body
        assert "Please choose..." in res.body, res.body

        self.login('root')
        params = {
                  '_repos':'project1',
                  'pluginid_0':'CaseInsensitive',
                  'pluginid_1':'EolStyleCheck',
                  }
        res = self.app.get(url(controller='repos', action="uninstall_hook"), params)
        assert res.status == "200 OK", res.status
        assert """<div class='info'>Delete plugin 'CaseInsensitive, EolStyleCheck' on 'project1' success.</div>""" == res.body, res.body

        self.login('root')
        params = {
                  'select':'project1', 
                  }
        res = self.app.get(url(controller='repos', action="get_plugin_list"), params)
        assert res.status == "200 OK", res.status
        assert "CaseInsensitive" in res.body, res.body
        assert "EolStyleCheck" in res.body, res.body
        assert "Please choose..." in res.body, res.body

        
    
