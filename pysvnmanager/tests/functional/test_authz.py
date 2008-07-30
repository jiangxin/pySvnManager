## -*- coding: utf-8 -*-

from pysvnmanager.tests import *
from pysvnmanager.controllers import authz

class TestAuthzController(TestController):
    def test_index(self):
        # Test redirect to login pange
        res = self.app.get(url_for(controller='authz'))
        assert res.status == 302
        self.assertEqual(res.header('location'), '/security')

        # Login as common user
        self.login('nobody')
        res = self.app.get(url_for(controller='authz'))
        assert res.status == 302
        self.assertEqual(res.header('location'), '/security/failed', res.header('location'))
        
        # Login as repos admin
        self.login('admin2')
        res = self.app.get(url_for(controller='authz'))
        assert res.status == 200
        assert res.c.reposlist == [u'repos1', u'repos2'], res.c.reposlist
        assert """<input type="button" name="save_btn"   value='Save'""" in res.body, res.body

        # Login as superuser
        self.login('root')
        res = self.app.get(url_for(controller='authz'))
        assert res.status == 200
        assert res.c.reposlist == ['/', u'repos1', u'repos2', u'repos3', u'document']
        assert """<input type="button" name="save_btn"   value='Save'""" in res.body, res.body

    def test_init_repos_list(self):
        # authn test
        res = self.app.get(url_for(controller='authz', action='init_repos_list'))
        assert res.status == 302
        self.assertEqual(res.header('location'), '/security')

        # authz test
        self.login('nobody')
        res = self.app.get(url_for(controller='authz', action='init_repos_list'))
        assert res.status == 302, res.status
        assert res.header('location')== '/security/failed', res.header('location')

        # Login as superuser
        self.login('root')
        res = self.app.get(url_for(controller='authz', action='init_repos_list'))
        assert res.status == 200
        assert """id[0]="...";name[0]="Please choose...";
id[1]="/";name[1]="/";
id[2]="repos1";name[2]="repos1";
id[3]="repos2";name[3]="repos2";
id[4]="repos3";name[4]="repos3";
id[5]="document";name[5]="document";
total=6;
revision="0.2.1";
""" == res.body, res.body
    
    def test_repos_changed(self):
        # authn test
        res = self.app.get(url_for(controller='authz', action='repos_changed'))
        assert res.status == 302
        self.assertEqual(res.header('location'), '/security')

        # authz test
        self.login('nobody')
        res = self.app.get(url_for(controller='authz', action='repos_changed'))
        assert res.status == 302, res.status
        assert res.header('location')== '/security/failed', res.header('location')

        # Login as superuser
        self.login('root')
        params = {'select':'/',}
        res = self.app.get(url_for(controller='authz', action='repos_changed'), params)
        assert res.status == 200
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
        res = self.app.get(url_for(controller='authz', action='repos_changed'), params)
        assert res.status == 200
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
        res = self.app.get(url_for(controller='authz', action='path_changed'))
        assert res.status == 302
        self.assertEqual(res.header('location'), '/security')

        # authz test
        self.login('nobody')
        res = self.app.get(url_for(controller='authz', action='path_changed'))
        assert res.status == 302, res.status
        assert res.header('location')== '/security/failed', res.header('location')

        self.login('root')
        params = {'reposname':'/', 'path':u'/tags//'}
        res = self.app.get(url_for(controller='authz', action='path_changed'), params)
        assert res.status == 200
        assert '''user[0]="&pm";
rights[0]="rw";
user[1]="$authenticated";
rights[1]="r";
total=2;
revision="0.2.1";
''' == res.body, res.body

        self.login('root')
        params = {'reposname':'document', 'path':'/trunk/商务部'}
        res = self.app.get(url_for(controller='authz', action='path_changed'), params)
        assert res.status == 200
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
        res = self.app.get(url_for(controller='authz', action='path_changed'), params)
        assert res.status == 200
        assert '' == res.body, res.body


    def test_set_repos_admin(self):
        # authn test
        try:
            res = self.app.get(url_for(controller='authz', action='save_authz'))
            assert res.status == 302
            self.assertEqual(res.header('location'), '/security')

            # authz test
            self.login('nobody')
            res = self.app.get(url_for(controller='authz', action='save_authz'))
            assert res.status == 302, res.status
            assert res.header('location')== '/security/failed', res.header('location')
            
            # Login as superuser
            self.login('root')
            params = {'reposname':'/', 'admins':''}
            res = self.app.get(url_for(controller='authz', action='save_authz'), params)
            assert res.status == 200
            assert "You can not delete yourself from admin list." == res.body, res.body
        finally:
            self.rollback()
            
        try:
            params = {'reposname':'/', 'admins':'root, @some'}
            res = self.app.get(url_for(controller='authz', action='save_authz'), params)
            assert res.status == 200
            assert "" == res.body, res.body
        finally:
            self.rollback()

        try:
            self.login('jiangxin')
            params = {'reposname':'/', 'admins':'&admin'}
            res = self.app.get(url_for(controller='authz', action='save_authz'), params)
            assert res.status == 200
            assert "" == res.body, res.body
        finally:
            self.rollback()
            
        try:
            self.login('jiangxin')
            params = {'reposname':'/', 'admins':'root'}
            res = self.app.get(url_for(controller='authz', action='save_authz'), params)
            assert res.status == 200
            assert "You can not delete yourself from admin list." == res.body, res.body
        finally:
            self.rollback()

        try:
            self.login('root')
            params = {'reposname':'/repos1', 'admins':'user1'}
            res = self.app.get(url_for(controller='authz', action='save_authz'), params)
            assert res.status == 200
            assert "" == res.body, res.body
        finally:
            self.rollback()
        
        try:
            self.login('root')
            params = {'reposname':'/repos1', 'admins':'user1, root'}
            res = self.app.get(url_for(controller='authz', action='save_authz'), params)
            assert res.status == 200
            assert "" == res.body, res.body
        finally:
            self.rollback()
        
        try:
            self.login('admin1')
            params = {'reposname':'/repos1', 'admins':'user1, root'}
            res = self.app.get(url_for(controller='authz', action='save_authz'), params)
            assert res.status == 200
            assert "You can not delete yourself from admin list." == res.body, res.body

            self.login('admin1')
            params = {'reposname':'/repos1', 'admins':'admin1, admin2'}
            res = self.app.get(url_for(controller='authz', action='save_authz'), params)
            assert res.status == 200
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
            res = self.app.get(url_for(controller='authz', action='save_authz'), params)
            assert res.status == 200
            assert "" == res.body, res.body
            
            authz = self.load_authz()
            module1 = authz.get_module('repos1', u'trunk/src')
            self.assert_(module1 != None, type(module1))
            self.assert_(unicode(module1)==u'[repos1:/trunk/src]\n&别名1 = r\n* = \n@管理员 = rw\nuser2 = r\n', unicode(module1).encode('utf-8'))
            
            # Test login using chinese username
            self.login('蒋鑫')
            params = {'reposname':'/repos1', 'path':'/trunk/src', 'admins':'其他', 'rules':'@管理员=rw\n&别名1=r\n*=\nuser2=r', 'mode1':'edit', 'mode2':'edit' }
            res = self.app.get(url_for(controller='authz', action='save_authz'), params)
            assert res.status == 200, res.headers
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
            res = self.app.get(url_for(controller='authz', action='save_authz'), params)
            assert res.status == 200
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
            res = self.app.get(url_for(controller='authz', action='save_authz'), params)
            assert res.status == 200
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
            res = self.app.get(url_for(controller='authz', action='save_authz'), params)
            assert res.status == 200
            assert "Repository reposX not exist." == res.body, res.body
        finally:
            self.rollback()
        
        # Test Repos/Module not exist Exception
        try:
            self.login('root')
            params = {'reposname':'repos1', 'path':'/trunk/myproject', 'admins':'蒋鑫', 'rules':'@管理员=rw\n&别名1=r\n*=\nuser2=r', 'mode1':'edit', 'mode2':'edit' }
            res = self.app.get(url_for(controller='authz', action='save_authz'), params)
            assert res.status == 200
            assert "Module /trunk/myproject not exist." == res.body, res.body
        finally:
            self.rollback()
        
        
    def test_delete_authz(self):
        # authn test
        res = self.app.get(url_for(controller='authz', action='delete_authz'))
        assert res.status == 302
        assert res.header('location')== '/security', res.header('location')

        # authz test
        self.login('nobody')
        res = self.app.get(url_for(controller='authz', action='delete_authz'))
        assert res.status == 302, res.status
        assert res.header('location')== '/security/failed', res.header('location')

        authz = self.load_authz()
        module1 = authz.get_module('document', u'/trunk/行政部')
        self.assert_(module1 != None, type(module1))
 
        self.login('root')
        params = {'reposname':'document', 'path':'/trunk/行政部'}
        res = self.app.get(url_for(controller='authz', action='delete_authz'), params)

        authz = self.load_authz()
        module1 = authz.get_module('document', u'/trunk/行政部')
        self.assert_(module1 == None, type(module1))        
        
        try:
            self.login('root')
            params = {'reposname':'document', 'path':'/trunk/行政部', 'revision':'123'}
            res = self.app.get(url_for(controller='authz', action='delete_authz'), params)
            assert res.status == 200
            assert "Update failed! You are working on a out-of-date revision." in res.body, res.body
        finally:
            self.rollback()
