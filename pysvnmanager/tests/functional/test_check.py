from pysvnmanager.tests import *
from pysvnmanager.controllers import check

class TestCheckController(TestController):

    def test_index(self):
        # Test redirect to login pange
        res = self.app.get(url_for(controller='check'))
        assert res.status == 302
        self.assertEqual(res.header('location'), '/login')

        # Login as common user
        self.login('nobody')
        res = self.app.get(url_for(controller='check'))
        assert res.status == 200
        assert 'Permission denied.' in res.body, res.body
        
        # Login as repos admin
        self.login('admin1')
        res = self.app.get(url_for(controller='check'))
        assert res.c.reposlist == [u'repos1'], res.c.reposlist

        # Login as repos admin
        self.login('admin2')
        res = self.app.get(url_for(controller='check'))
        assert res.c.reposlist == [u'repos1', u'repos2'], res.c.reposlist

        # Login as superuser
        self.login('root')
        res = self.app.get(url_for(controller='check'))
        assert res.status == 200
        assert '''<input type="submit" name="submit" value='Check Permissions'>''' in res.body
        assert res.c.reposlist == ['/', u'repos1', u'repos2', u'repos3', u'document']


    def test_path_authz(self):
        # Login as superuser
        self.login('root')
        params = {
                  'userinput':'select', 
                  'userselector':'user1',
                  'reposinput':'select', 
                  'reposselector':'///repos1',
                  'pathinput':'manual',
                  'pathname':'/trunk/src/test',
                  'abbr':'True',
                  }
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert res.status == 200
        assert res.c.reposlist == ['/', u'repos1', u'repos2', u'repos3', u'document'], res.c.reposlist
        assert '''<div id='acl_path_msg'>[repos1:/trunk/src/test] user1 =</div>''' in res.body, res.body

        params['userselector'] = 'user1'
        params['reposselector'] = 'reposX'
        params['pathname'] = '/trunk/src/test'
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[reposX:/trunk/src/test] user1 = r</div>''' in res.body, res.body

        params['userselector'] = 'user2'
        params['reposselector'] = 'repos1'
        params['pathname'] = '/trunk/src/test'
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[repos1:/trunk/src/test] user2 = r</div>''' in res.body, res.body

        params['userselector'] = 'user2'
        params['reposselector'] = 'reposX'
        params['pathname'] = '/trunk/'
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[reposX:/trunk] user2 =</div>''' in res.body, res.body

        params['userselector'] = 'user3'
        params['reposselector'] = 'repos1'
        params['pathname'] = '/trunk'
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[repos1:/trunk] user3 =</div>''' in res.body, res.body

        params['userselector'] = 'user4'
        params['reposselector'] = 'repos1'
        params['pathname'] = '/trunk'
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[repos1:/trunk] user4 = r</div>''' in res.body, res.body

        params['userselector'] = 'user4'
        params['reposselector'] = 'reposX'
        params['pathname'] = '/trunk'
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[reposX:/trunk] user4 = r</div>''' in res.body, res.body

        params['userselector'] = 'user5'
        params['reposselector'] = 'reposX'
        params['pathname'] = '/trunk'
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[reposX:/trunk] user5 =</div>''' in res.body, res.body


    def test_access_map(self):
        # Test redirect to login pange
        res = self.app.get(url_for(controller='check', action='access_map'))
        assert res.status == 302
        self.assertEqual(res.header('location'), '/login')

        # Login as common user
        self.login('nobody')
        res = self.app.get(url_for(controller='check', action='access_map'))
        assert res.status == 200
        assert 'Permission denied.' in res.body, res.body

        # Login as common user
        self.login('admin1')
        res = self.app.get(url_for(controller='check', action='access_map'))
        assert res.status == 200
        assert 'Permission denied.' == res.body, res.body
        
        params = {
                  'userinput':'select', 
                  'userselector':'user1',
                  'reposinput':'select', 
                  'reposselector':'repos1',
                  'pathinput':'manual',
                  'pathname':'/trunk/src/test',
                  'abbr':'True',
                  }
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert res.status == 200
        assert res.c.reposlist == [u'repos1'], res.c.reposlist
        assert '''<div id='acl_path_msg'>[repos1:/trunk/src/test] user1 =</div>''' in res.body, res.body

        params['reposselector'] = 'reposX'
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert 'Permission denied.' == res.body, res.body
