from pysvnmanager.tests import *
from pysvnmanager.controllers import role

class TestRoleController(TestController):

    def test_index(self):
        # Test redirect to login pange
        res = self.app.get(url_for(controller='role'))
        assert res.status == 302
        self.assertEqual(res.header('location'), '/login')

        # Login as common user
        self.login('nobody')
        res = self.app.get(url_for(controller='role'))
        assert res.status == 200
        assert 'Permission denied.' in res.body, res.body
        
        # Permission denied for repos admin(not root admin)
        self.login('admin2')
        res = self.app.get(url_for(controller='role'))
        assert res.status == 200
        assert "Permission denied." in res.body, res.body

        # Login as superuser
        self.login('root')
        res = self.app.get(url_for(controller='role'))
        assert res.status == 200
        assert """<input type="button" name="save_btn"   value='Save'""" in res.body, res.body

    def test_get_role_info(self):
        # Login as superuser
        self.login('root')
        params = {'role':'',}
        res = self.app.get(url_for(controller='role', action='get_role_info'), params)
        assert res.status == 200
        assert """id[0]="...";name[0]="Please choose...";
id[1]="@admin";name[1]="Group:admin";
id[2]="@all";name[2]="Group:all";
id[3]="@dev";name[3]="Group:dev";
id[4]="@test";name[4]="Group:test";
id[5]="@biz";name[5]="Group:biz";
id[6]="@group1";name[6]="Group:group1";
id[7]="@group2";name[7]="Group:group2";
id[8]="@group3";name[8]="Group:group3";
id[9]="@office";name[9]="Group:office";
id[10]="@tech";name[10]="Group:tech";
id[11]="&admin";name[11]="Alias:admin";
id[12]="&pm";name[12]="Alias:pm";
id[13]="&tm";name[13]="Alias:tm";
members_count=14;
revision="0.2.1";
""" == res.body, res.body

        params = {'role':'@admin',}
        res = self.app.get(url_for(controller='role', action='get_role_info'), params)
        assert res.status == 200
        assert """id[0]="&admin";name[0]="Alias:admin";
id[1]="admin1";name[1]="admin1";
id[2]="admin2";name[2]="admin2";
id[3]="admin3";name[3]="admin3";
members_count=4;
revision="0.2.1";
""" == res.body, res.body

        params = {'role':'@group3',}
        res = self.app.get(url_for(controller='role', action='get_role_info'), params)
        assert res.status == 200
        assert """id[0]="user3";name[0]="user3";
id[1]="user31";name[1]="user31";
id[2]="user32";name[2]="user32";
members_count=3;
revision="0.2.1";
""" == res.body, res.body

        params = {'role':'&admin',}
        res = self.app.get(url_for(controller='role', action='get_role_info'), params)
        assert res.status == 200
        assert """aliasname = "&admin";username = "jiangxin";
revision="0.2.1";
""" == res.body, res.body

    def test_save_group(self):
        pass

    def test_delete_group(self):
        pass

    def test_save_alias(self):
        pass

    def test_delete_alias(self):
        pass

