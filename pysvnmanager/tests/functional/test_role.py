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
from pysvnmanager.controllers import role

class TestRoleController(TestController):

    def test_index(self):
        # Test redirect to login pange
        res = self.app.get(url(controller='role', action='index'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/login'), res.location

        # Login as common user
        self.login('nobody')
        res = self.app.get(url(controller='role', action='index'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/security/failed'), res.location
        
        # Repos admin(not root admin) can access role controller, but with disabled button.
        self.login('admin2')
        res = self.app.get(url(controller='role', action='index'))
        assert res.status == "200 OK", res.status
        assert """
    <input type="button" name="save_btn"   value='Save'  onClick="do_save(this.form)" DISABLED>
    <input type="button" name="delete_btn" value='Delete' onClick="do_delete(this.form)" DISABLED>
    <input type="button" name="cancel_btn" value='Cancel' onClick="role_changed()" DISABLED>""" in res.body, res.body[-300:]

        # Login as superuser
        self.login('root')
        res = self.app.get(url(controller='role', action='index'))
        assert res.status == "200 OK", res.status
        assert """<input type="button" name="save_btn"   value='Save'""" in res.body, res.body

    def test_get_role_info(self):
        # authn test
        res = self.app.get(url(controller='role', action='get_role_info'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/login'), res.location

        # authz test
        self.login('nobody')
        res = self.app.get(url(controller='role', action='get_role_info'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/security/failed'), res.location
        
        # Login as superuser
        self.login('root')
        params = {'role':'',}
        res = self.app.get(url(controller='role', action='get_role_info'), params)
        assert res.status == "200 OK", res.status
        assert """id[0]="...";name[0]="Please choose...";
id[1]="@admin";name[1]="Group:admin";
id[2]="@all";name[2]="Group:all";
id[3]="@biz";name[3]="Group:biz";
id[4]="@dev";name[4]="Group:dev";
id[5]="@group1";name[5]="Group:group1";
id[6]="@group2";name[6]="Group:group2";
id[7]="@group3";name[7]="Group:group3";
id[8]="@office";name[8]="Group:office";
id[9]="@tech";name[9]="Group:tech";
id[10]="@test";name[10]="Group:test";
id[11]="&admin";name[11]="Alias:admin";
id[12]="&pm";name[12]="Alias:pm";
id[13]="&tm";name[13]="Alias:tm";
members_count=14;
revision="0.2.1";
""" == res.body, res.body

        params = {'role':'@admin',}
        res = self.app.get(url(controller='role', action='get_role_info'), params)
        assert res.status == "200 OK", res.status
        assert """id[0]="&admin";name[0]="Alias:admin";
id[1]="admin1";name[1]="admin1";
id[2]="admin2";name[2]="admin2";
id[3]="admin3";name[3]="admin3";
members_count=4;
revision="0.2.1";
""" == res.body, res.body

        params = {'role':'@group1',}
        res = self.app.get(url(controller='role', action='get_role_info'), params)
        assert res.status == "200 OK", res.status
        assert """id[0]="@group2";name[0]="Group:group2";
id[1]="@group3";name[1]="Group:group3";
id[2]="user1";name[2]="user1";
id[3]="user11";name[3]="user11";
id[4]="user12";name[4]="user12";
members_count=5;
revision="0.2.1";
""" == res.body, res.body

        params = {'role':'@group3',}
        res = self.app.get(url(controller='role', action='get_role_info'), params)
        assert res.status == "200 OK", res.status
        assert """id[0]="user3";name[0]="user3";
id[1]="user31";name[1]="user31";
id[2]="user32";name[2]="user32";
members_count=3;
revision="0.2.1";
""" == res.body, res.body

        params = {'role':'&admin',}
        res = self.app.get(url(controller='role', action='get_role_info'), params)
        assert res.status == "200 OK", res.status
        assert """aliasname = "&admin";username = "jiangxin";
revision="0.2.1";
""" == res.body, res.body

    def test_save_group(self):
        # authn test
        res = self.app.get(url(controller='role', action='save_group'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/login'), res.location

        # authz test
        self.login('nobody')
        res = self.app.get(url(controller='role', action='save_group'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/security/failed'), res.location


        # Change group members, autodrop=no
        try:
            authz = self.load_authz()
            userobj = authz.get_userobj('@group3')
            self.assert_(unicode(userobj) == u'group3 = user3, user31, user32', unicode(userobj).encode('utf-8'))

            self.login('root')
            params = {'rolename':'group3', 'members':'蒋鑫, user3,@group1', 'autodrop':'no', }
            res = self.app.get(url(controller='role', action='save_group'), params)
            assert res.status == "200 OK", res.status
            assert "Recursive group membership for @group1" in res.body, res.body
        
            authz = self.load_authz()
            userobj = authz.get_userobj('@group3')
            self.assert_(unicode(userobj) == u'group3 = user3, user31, user32', unicode(userobj).encode('utf-8'))
        finally:
            self.rollback()

        # Change group members, autodrop=yes
        try:
            authz = self.load_authz()
            userobj = authz.get_userobj('@group3')
            self.assert_(unicode(userobj) == u'group3 = user3, user31, user32', unicode(userobj).encode('utf-8'))

            self.login('root')
            params = {'rolename':'group3', 'members':'蒋鑫, user3,@group1', 'autodrop':'yes', }
            res = self.app.get(url(controller='role', action='save_group'), params)
            assert res.status == "200 OK", res.status
            assert "" == res.body, res.body
        
            authz = self.load_authz()
            userobj = authz.get_userobj('@group3')
            self.assert_(unicode(userobj) == u'group3 = user3, 蒋鑫', unicode(userobj).encode('utf-8'))
        finally:
            self.rollback()

        # Add New Group
        try:
            authz = self.load_authz()
            userobj = authz.get_userobj('@管理员组')
            self.assert_(userobj == None)

            self.login('root')
            params = {'rolename':'管理员组', 'members':'蒋鑫, user3,@group1' }
            res = self.app.get(url(controller='role', action='save_group'), params)
            assert res.status == "200 OK", res.status
            assert "" == res.body, res.body
        
            authz = self.load_authz()
            userobj = authz.get_userobj('@管理员组')
            self.assert_(unicode(userobj) == u'管理员组 = @group1, user3, 蒋鑫', unicode(userobj).encode('utf-8'))
        finally:
            self.rollback()

        # Add New Group, out-of-date
        try:
            authz = self.load_authz()
            userobj = authz.get_userobj('@管理员组')
            self.assert_(userobj == None)

            self.login('root')
            params = {'rolename':'管理员组', 'members':'蒋鑫, user3,@group1', 'revision':'' }
            res = self.app.get(url(controller='role', action='save_group'), params)
            assert res.status == "200 OK", res.status
            assert "Update failed! You are working on a out-of-date revision." in res.body, res.body
        
            authz = self.load_authz()
            userobj = authz.get_userobj('@管理员组')
            self.assert_(userobj == None)
        finally:
            self.rollback()
            
    def test_delete_group(self):
        # authn test
        res = self.app.get(url(controller='role', action='delete_group'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/login'), res.location

        # authz test
        self.login('nobody')
        res = self.app.get(url(controller='role', action='delete_group'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/security/failed'), res.location

        # Delete group failed, ref by other group.
        try:
            authz = self.load_authz()
            userobj = authz.get_userobj('@group3')
            self.assert_(unicode(userobj) == u'group3 = user3, user31, user32', unicode(userobj).encode('utf-8'))

            self.login('root')
            params = {'role':'group3',}
            res = self.app.get(url(controller='role', action='delete_group'), params)
            assert res.status == "200 OK", res.status
            assert "Group group3 is referenced by group @group1." in res.body, res.body
        finally:
            self.rollback()

        # Delete group failed, ref by rules.
        try:
            authz = self.load_authz()
            userobj = authz.get_userobj('@dev')
            self.assert_(unicode(userobj) == u'dev = dev1, dev2, dev3', unicode(userobj).encode('utf-8'))

            self.login('root')
            params = {'role':'@dev',}
            res = self.app.get(url(controller='role', action='delete_group'), params)
            assert res.status == "200 OK", res.status
            assert "@dev is referenced by [/:/trunk]." in res.body, res.body
        
            authz = self.load_authz()
            userobj = authz.get_userobj('@dev')
            self.assert_(unicode(userobj) == u'dev = dev1, dev2, dev3', unicode(userobj).encode('utf-8'))
        finally:
            self.rollback()

        # Delete group successful.
        try:
            authz = self.load_authz()
            userobj = authz.get_userobj('@all')
            self.assert_(unicode(userobj) == 'all = @admin, @dev, @test', unicode(userobj).encode('utf-8'))

            self.login('root')
            params = {'role':'all',}
            res = self.app.get(url(controller='role', action='delete_group'), params)
            assert res.status == "200 OK", res.status
            assert "" == res.body, res.body
        
            authz = self.load_authz()
            userobj = authz.get_userobj('@all')
            self.assert_(userobj==None)
        finally:
            self.rollback()

    def test_save_alias(self):
        # authn test
        res = self.app.get(url(controller='role', action='save_alias'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/login'), res.location

        # authz test
        self.login('nobody')
        res = self.app.get(url(controller='role', action='save_alias'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/security/failed'), res.location

        # Change alias successfully
        try:
            authz = self.load_authz()
            userobj = authz.get_userobj('&admin')
            self.assert_(unicode(userobj) == u'admin = jiangxin', unicode(userobj).encode('utf-8'))

            self.login('root')
            params = {'aliasname':'admin', 'username':'蒋鑫',}
            res = self.app.get(url(controller='role', action='save_alias'), params)
            assert res.status == "200 OK", res.status
            assert "" == res.body, res.body
        
            authz = self.load_authz()
            userobj = authz.get_userobj('&admin')
            self.assert_(unicode(userobj) == u'admin = 蒋鑫', unicode(userobj).encode('utf-8'))
            self.assert_(authz.is_super_user('&admin')==True, authz.is_super_user('&admin'))
            self.assert_(authz.is_super_user('蒋鑫')==True, authz.is_super_user('蒋鑫'))
            
            self.login('蒋鑫')
            #params = {'aliasname':'admin', 'username':'蒋鑫',}
            params = {'aliasname':'admin2', 'username':'jiangxin',}
            res = self.app.get(url(controller='role', action='save_alias'), params)
            assert res.status == "200 OK", res.status
            assert "" == res.body, res.body
            
        finally:
            self.rollback()
            
        # Add new alias successfully
        try:
            authz = self.load_authz()
            userobj = authz.get_userobj('&管理员')
            self.assert_(userobj == None)

            self.login('root')
            params = {'aliasname':'管理员', 'username':'蒋鑫',}
            res = self.app.get(url(controller='role', action='save_alias'), params)
            assert res.status == "200 OK", res.status
            assert "" == res.body, res.body
        
            authz = self.load_authz()
            userobj = authz.get_userobj('&管理员')
            self.assert_(unicode(userobj) == u'管理员 = 蒋鑫', unicode(userobj).encode('utf-8'))
        finally:
            self.rollback()
            
        # Change alias failed, out-of-date
        try:
            authz = self.load_authz()
            userobj = authz.get_userobj('&admin')
            self.assert_(unicode(userobj) == u'admin = jiangxin', unicode(userobj).encode('utf-8'))

            self.login('root')
            params = {'aliasname':'admin', 'username':'蒋鑫', 'revision':'123'}
            res = self.app.get(url(controller='role', action='save_alias'), params)
            assert res.status == "200 OK", res.status
            assert "Update failed! You are working on a out-of-date revision." in res.body, res.body
        
            authz = self.load_authz()
            userobj = authz.get_userobj('&admin')
            self.assert_(unicode(userobj) == u'admin = jiangxin', unicode(userobj).encode('utf-8'))
        finally:
            self.rollback()
            
            
    def test_delete_alias(self):
        # authn test
        res = self.app.get(url(controller='role', action='delete_alias'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/login'), res.location

        # authz test
        self.login('nobody')
        res = self.app.get(url(controller='role', action='delete_alias'))
        assert res.status == "302 Found", res.status
        assert res.location.endswith('/security/failed'), res.location

        # Delete alias successfully
        try:
            authz = self.load_authz()
            userobj = authz.get_userobj('&tm')
            self.assert_(unicode(userobj) == u'tm = test1', unicode(userobj).encode('utf-8'))

            self.login('root')
            params = {'aliasname':'tm'}
            res = self.app.get(url(controller='role', action='delete_alias'), params)
            assert res.status == "200 OK", res.status
            assert "" == res.body, res.body
        
            authz = self.load_authz()
            userobj = authz.get_userobj('&tm')
            self.assert_(userobj == None)
        finally:
            self.rollback()
            
        # Delete alias failed. out of date
        try:
            authz = self.load_authz()
            userobj = authz.get_userobj('&tm')
            self.assert_(unicode(userobj) == u'tm = test1', unicode(userobj).encode('utf-8'))

            self.login('root')
            params = {'aliasname':'tm', 'revision':''}
            res = self.app.get(url(controller='role', action='delete_alias'), params)
            assert res.status == "200 OK", res.status
            assert "Update failed! You are working on a out-of-date revision." in res.body, res.body
        
            authz = self.load_authz()
            userobj = authz.get_userobj('&tm')
            self.assert_(unicode(userobj) == u'tm = test1', unicode(userobj).encode('utf-8'))
        finally:
            self.rollback()
            

        # Delete alias failed. refenced by rules.
        try:
            authz = self.load_authz()
            userobj = authz.get_userobj('&pm')
            self.assert_(unicode(userobj) == u'pm = dev1', unicode(userobj).encode('utf-8'))

            self.login('root')
            params = {'aliasname':'pm', 'revision':''}
            res = self.app.get(url(controller='role', action='delete_alias'), params)
            assert res.status == "200 OK", res.status
            assert "&pm is referenced by [/:/trunk]." in res.body, res.body
        
            authz = self.load_authz()
            userobj = authz.get_userobj('&pm')
            self.assert_(unicode(userobj) == u'pm = dev1', unicode(userobj).encode('utf-8'))
        finally:
            self.rollback()
