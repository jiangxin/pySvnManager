from pysvnmanager.tests import *
from pysvnmanager.controllers import authz

class TestAuthzController(TestController):
    def test_index(self):
        # Test redirect to login pange
        res = self.app.get(url_for(controller='authz'))
        assert res.status == 302
        self.assertEqual(res.header('location'), '/login')

        # Login as common user
        self.login('nobody')
        res = self.app.get(url_for(controller='authz'))
        assert res.status == 200
        assert 'Permission denied.' in res.body, res.body
        
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

    def test_delete_admin(self):
        # Login as superuser
        self.login('root')
        params = {'reposname':'/', 'admins':''}
        res = self.app.get(url_for(controller='authz', action='save_authz'), params)
        assert res.status == 200
        assert "You can not delete yourself from admin list." == res.body, res.body
        self.rollback()
        
        params = {'reposname':'/', 'admins':'root, @some'}
        res = self.app.get(url_for(controller='authz', action='save_authz'), params)
        assert res.status == 200
        assert "" == res.body, res.body
        self.rollback()

        self.login('jiangxin')
        params = {'reposname':'/', 'admins':'&admin'}
        res = self.app.get(url_for(controller='authz', action='save_authz'), params)
        assert res.status == 200
        assert "" == res.body, res.body
        self.rollback()
        
        params = {'reposname':'/', 'admins':'root'}
        res = self.app.get(url_for(controller='authz', action='save_authz'), params)
        assert res.status == 200
        assert "You can not delete yourself from admin list." == res.body, res.body
        self.rollback()



        
        self.login('root')
        params = {'reposname':'/repos1', 'admins':'user1'}
        res = self.app.get(url_for(controller='authz', action='save_authz'), params)
        #assert res.status == 200
        #assert "" == res.body, res.body
        self.rollback()
    
        self.login('root')
        params = {'reposname':'/repos1', 'admins':'user1, root'}
        res = self.app.get(url_for(controller='authz', action='save_authz'), params)
        #assert res.status == 200
        #assert "" == res.body, res.body
        self.rollback()
    
        self.login('admin1')
        params = {'reposname':'/repos1', 'admins':'user1, root'}
        res = self.app.get(url_for(controller='authz', action='save_authz'), params)
        #assert res.status == 200
        #assert "You can not delete yourself from admin list." == res.body, res.body

        self.login('admin1')
        params = {'reposname':'/repos1', 'admins':'admin1, admin2'}
        res = self.app.get(url_for(controller='authz', action='save_authz'), params)
        #assert res.status == 200
        #assert "" == res.body, res.body
        self.rollback()
    

    def test_save_authz(self):
        pass
    
    def test_delete_authz(self):
        pass
        
