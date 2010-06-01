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
from pysvnmanager.controllers import authz

class TestAuthzController(TestController):
    def test_index(self):
        # Test redirect to login pange
        res = self.app.get(url(controller='authz', action='index'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/login'), res

        # Login as common user
        self.login('nobody')
        res = self.app.get(url(controller='authz', action='index'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/security/failed'), res.header
        
        # Login as repos admin
        self.login('admin2')
        res = self.app.get(url(controller='authz', action='index'))
        assert res.status == "200 OK", res.status
        assert ','.join(sorted(res.tmpl_context.reposlist)) == 'repos1,repos2', res.tmpl_context.reposlist
        assert """<input type="button" name="save_btn"   value='Save'""" in res.body, res.body

        # Login as superuser
        self.login('root')
        res = self.app.get(url(controller='authz', action='index'))
        assert res.status == "200 OK", res.status
        assert ','.join(sorted(res.tmpl_context.reposlist)) == u'/,document,repos1,repos2,repos3', res.tmpl_context.reposlist
        assert """<input type="button" name="save_btn"   value='Save'""" in res.body, res.body

    def test_init_repos_list(self):
        # authn test
        res = self.app.get(url(controller='authz', action='init_repos_list'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/login'), res.location

        # authz test
        self.login('nobody')
        res = self.app.get(url(controller='authz', action='init_repos_list'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/security/failed'), res.location

        # Login as superuser
        self.login('root')
        res = self.app.get(url(controller='authz', action='init_repos_list'))
        assert res.status == "200 OK", res.status
        assert """id[0]="...";name[0]="Please choose...";
id[1]="/";name[1]="/";
id[2]="repos3";name[2]="repos3";
id[3]="document";name[3]="document (?)";
id[4]="repos1";name[4]="repos1 (?)";
id[5]="repos2";name[5]="repos2 (?)";
id[6]="project1";name[6]="project1 (!)";
id[7]="project2";name[7]="project2 (!)";
total=8;
revision="0.2.1";
""" == res.body, res.body
    
    def test_repos_changed(self):
        # authn test
        res = self.app.get(url(controller='authz', action='repos_changed'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/login'), res.location

        # authz test
        self.login('nobody')
        res = self.app.get(url(controller='authz', action='repos_changed'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/security/failed'), res.location

        # Login as superuser
        self.login('root')
        params = {'select':'/',}
        res = self.app.get(url(controller='authz', action='repos_changed'), params)
        assert res.status == "200 OK", res.status
        assert '''id[0]="...";name[0]="Please choose...";
id[1]="/trunk/src";name[1]="/trunk/src";
id[2]="/trunk";name[2]="/trunk";
id[3]="/";name[3]="/";
id[4]="/tags";name[4]="/tags";
id[5]="/branches";name[5]="/branches";
total=6;
admin_users="&admin, root";
revision="0.2.1";
''' == res.body, res.body

        params = {'select':'repos1',}
        res = self.app.get(url(controller='authz', action='repos_changed'), params)
        assert res.status == "200 OK", res.status
        assert '''id[0]="...";name[0]="Please choose...";
id[1]="/trunk/src";name[1]="/trunk/src";
id[2]="/trunk";name[2]="/trunk";
id[3]="/";name[3]="/";
total=4;
admin_users="@admin";
revision="0.2.1";
''' == res.body, res.body

    def test_path_changed(self):
        params={}
        # authn test
        res = self.app.get(url(controller='authz', action='path_changed'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/login'), res.location

        # authz test
        self.login('nobody')
        res = self.app.get(url(controller='authz', action='path_changed'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/security/failed'), res.location

        self.login('root')
        params = {'reposname':'/', 'path':u'/tags//'}
        res = self.app.get(url(controller='authz', action='path_changed'), params)
        assert res.status == "200 OK", res.status
        assert '''user[0]="&pm";
rights[0]="rw";
user[1]="$authenticated";
rights[1]="r";
total=2;
revision="0.2.1";
''' == res.body, res.body

        self.login('root')
        params = {'reposname':'document', 'path':'/trunk/商务部'}
        res = self.app.get(url(controller='authz', action='path_changed'), params)
        assert res.status == "200 OK", res.status
        assert '''user[0]="*";
rights[0]="";
user[1]="@admin";
rights[1]="rw";
user[2]="@biz";
rights[2]="rw";
total=3;
revision="0.2.1";
''' == res.body, res.body

        self.login('root')
        params = {'reposname':'/', 'path':'/noexist'}
        res = self.app.get(url(controller='authz', action='path_changed'), params)
        assert res.status == "200 OK", res.status
        assert '' == res.body, res.body


    def test_set_repos_admin(self):
        # authn test
        try:
            res = self.app.get(url(controller='authz', action='save_authz'))
            assert res.status == "302 Found", res.status
            assert res.location.endswith('/login'), res.location

            # authz test
            self.login('nobody')
            res = self.app.get(url(controller='authz', action='save_authz'))
            assert res.status == "302 Found", res.status
            assert res.location.endswith('/security/failed'), res.location
            
            # Login as superuser
            self.login('root')
            params = {'reposname':'/', 'admins':''}
            res = self.app.get(url(controller='authz', action='save_authz'), params)
            assert res.status == "200 OK", res.status
            assert "You can not delete yourself from admin list." == res.body, res.body
        finally:
            self.rollback()
            
        try:
            params = {'reposname':'/', 'admins':'root, @some'}
            res = self.app.get(url(controller='authz', action='save_authz'), params)
            assert res.status == "200 OK", res.status
            assert "" == res.body, res.body
        finally:
            self.rollback()

        try:
            self.login('jiangxin')
            params = {'reposname':'/', 'admins':'&admin'}
            res = self.app.get(url(controller='authz', action='save_authz'), params)
            assert res.status == "200 OK", res.status
            assert "" == res.body, res.body
        finally:
            self.rollback()
            
        try:
            self.login('jiangxin')
            params = {'reposname':'/', 'admins':'root'}
            res = self.app.get(url(controller='authz', action='save_authz'), params)
            assert res.status == "200 OK", res.status
            assert "You can not delete yourself from admin list." == res.body, res.body
        finally:
            self.rollback()

        try:
            self.login('root')
            params = {'reposname':'/repos1', 'admins':'user1'}
            res = self.app.get(url(controller='authz', action='save_authz'), params)
            assert res.status == "200 OK", res.status
            assert "" == res.body, res.body
        finally:
            self.rollback()
        
        try:
            self.login('root')
            params = {'reposname':'/repos1', 'admins':'user1, root'}
            res = self.app.get(url(controller='authz', action='save_authz'), params)
            assert res.status == "200 OK", res.status
            assert "" == res.body, res.body
        finally:
            self.rollback()
        
        try:
            self.login('admin1')
            params = {'reposname':'/repos1', 'admins':'user1, root'}
            res = self.app.get(url(controller='authz', action='save_authz'), params)
            assert res.status == "200 OK", res.status
            assert "You can not delete yourself from admin list." == res.body, res.body

            self.login('admin1')
            params = {'reposname':'/repos1', 'admins':'admin1, admin2'}
            res = self.app.get(url(controller='authz', action='save_authz'), params)
            assert res.status == "200 OK", res.status
            assert "" == res.body, res.body
        finally:
            self.rollback()

    def test_set_rules(self):
        # Modify rules for repos
        try:
            authz = self.load_authz()
            module1 = authz.get_module('repos1', u'trunk/src')
            self.assert_(module1 != None, type(module1))
            self.assert_(unicode(module1)=='[repos1:/trunk/src]\nuser1 = \n', unicode(module1).encode('utf-8'))

            self.login('root')
            params = {'reposname':'/repos1', 'path':'/trunk/src', 'admins':'蒋鑫', 'rules':'@管理员=rw\n&别名1=r\n*=\nuser2=r', 'mode1':'edit', 'mode2':'edit' }
            res = self.app.get(url(controller='authz', action='save_authz'), params)
            assert res.status == "200 OK", res.status
            assert "" == res.body, res.body
            
            authz = self.load_authz()
            module1 = authz.get_module('repos1', u'trunk/src')
            self.assert_(module1 != None, type(module1))
            self.assert_(unicode(module1)==u'[repos1:/trunk/src]\n&别名1 = r\n* = \n@管理员 = rw\nuser2 = r\n', unicode(module1).encode('utf-8'))
            
            # Test login using chinese username
            self.login('蒋鑫')
            params = {'reposname':'/repos1', 'path':'/trunk/src', 'admins':'其他', 'rules':'@管理员=rw\n&别名1=r\n*=\nuser2=r', 'mode1':'edit', 'mode2':'edit' }
            res = self.app.get(url(controller='authz', action='save_authz'), params)
            assert res.status == "200 OK", res.headers
            assert "You can not delete yourself from admin list." in res.body, res.body
        finally:
            self.rollback()

        # Add New Repos
        try:
            authz = self.load_authz()
            repos1 = authz.get_repos('reposX')
            self.assert_(repos1 == None, type(repos1))

            self.login('root')
            params = {'reposname':'reposX', 'admins':'蒋鑫', 'rules':'@管理员=rw\n&别名1=r\n*=\nuser2=r', 'mode1':'new', 'mode2':'new' }
            res = self.app.get(url(controller='authz', action='save_authz'), params)
            assert res.status == "200 OK", res.status
            assert "" == res.body, res.body
        
            authz = self.load_authz()
            repos1 = authz.get_repos('reposX')
            self.assert_(repos1 != None, type(repos1))
            self.assert_(unicode(repos1)==u'', unicode(repos1).encode('utf-8'))
            self.assert_(repos1.admins==u'蒋鑫', repos1.admins.encode('utf-8'))
        finally:
            self.rollback()

        # Add New Repos with Module/Rules
        try:
            authz = self.load_authz()
            repos1 = authz.get_repos('reposX')
            self.assert_(repos1 == None, type(repos1))

            self.login('root')
            params = {'reposname':'reposX', 'admins':'蒋鑫', 'path':'/项目a', 'rules':'@管理员=rw\n&别名1=r\n*=\nuser2=r', 'mode1':'new', 'mode2':'new' }
            res = self.app.get(url(controller='authz', action='save_authz'), params)
            assert res.status == "200 OK", res.status
            assert "" == res.body, res.body
        
            authz = self.load_authz()
            repos1 = authz.get_repos('reposX')
            self.assert_(unicode(repos1)==u'[reposX:/项目a]\n&别名1 = r\n* = \n@管理员 = rw\nuser2 = r\n\n', unicode(repos1).encode('utf-8'))
            self.assert_(repos1.admins==u'蒋鑫', repos1.admins.encode('utf-8'))
        finally:
            self.rollback()
        
        # Test Repos/Module not exist Exception
        try:
            self.login('root')
            params = {'reposname':'reposX', 'path':'/trunk/src', 'admins':'蒋鑫', 'rules':'@管理员=rw\n&别名1=r\n*=\nuser2=r', 'mode1':'edit', 'mode2':'edit' }
            res = self.app.get(url(controller='authz', action='save_authz'), params)
            assert res.status == "200 OK", res.status
            assert "Module /trunk/src not exist." == res.body, res.body
        finally:
            self.rollback()
        
        # Test Repos/Module not exist Exception
        try:
            self.login('root')
            params = {'reposname':'repos1', 'path':'/trunk/myproject', 'admins':'蒋鑫', 'rules':'@管理员=rw\n&别名1=r\n*=\nuser2=r', 'mode1':'edit', 'mode2':'edit' }
            res = self.app.get(url(controller='authz', action='save_authz'), params)
            assert res.status == "200 OK", res.status
            assert "Module /trunk/myproject not exist." == res.body, res.body
        finally:
            self.rollback()
        
        
    def test_delete_authz(self):
        # authn test
        res = self.app.get(url(controller='authz', action='delete_authz'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/login'), res.location

        # authz test
        self.login('nobody')
        res = self.app.get(url(controller='authz', action='delete_authz'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/security/failed'), res.location

        authz = self.load_authz()
        module1 = authz.get_module('document', u'/trunk/行政部')
        self.assert_(module1 != None, type(module1))
 
        self.login('root')
        params = {'reposname':'document', 'path':'/trunk/行政部'}
        res = self.app.get(url(controller='authz', action='delete_authz'), params)

        authz = self.load_authz()
        module1 = authz.get_module('document', u'/trunk/行政部')
        self.assert_(module1 == None, type(module1))        
        
        try:
            self.login('root')
            params = {'reposname':'document', 'path':'/trunk/行政部', 'revision':'123'}
            res = self.app.get(url(controller='authz', action='delete_authz'), params)
            assert res.status == "200 OK", res.status
            assert "Update failed! You are working on a out-of-date revision." in res.body, res.body
        finally:
            self.rollback()
