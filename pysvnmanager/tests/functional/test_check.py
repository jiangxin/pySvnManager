## -*- coding: utf-8 -*-

from pysvnmanager.tests import *
from pysvnmanager.controllers import check

class TestCheckController(TestController):

    def test_index(self):
        # Test redirect to login pange
        res = self.app.get(url_for(controller='check'))
        assert res.status == 302
        self.assertEqual(res.header('location'), '/security')

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


    def test_access_map(self):
        # authn test
        res = self.app.get(url_for(controller='check', action='access_map'))
        assert res.status == 302
        self.assertEqual(res.header('location'), '/security')

        # authz test
        self.login('nobody')
        res = self.app.get(url_for(controller='check', action='access_map'))
        assert res.status == 200, res.status
        self.assert_('Permission denied.' in res.body, res.body)
        
        # Login as superuser
        self.login('root')
        params = {
                  'userinput':'select', 
                  'userselector':'user1',
                  'reposinput':'select', 
                  'reposselector':'///repos1',
                  'pathinput':'select',
                  'pathselector':'/trunk/src/test',
                  'abbr':'True',
                  }
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert res.status == 200
        assert '''<div id='acl_path_msg'>[repos1:/trunk/src/test] user1 =</div>''' in res.body, res.body

        params['userinput'] = 'select'
        params['reposinput'] = 'select'
        params['pathinput'] = 'select'
        params['userselector'] = 'user1'
        params['reposselector'] = 'reposX'
        params['pathselector'] = '/trunk/src/test'
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[reposX:/trunk/src/test] user1 = r</div>''' in res.body, res.body

        params['userinput'] = 'manual'
        params['reposinput'] = 'manual'
        params['pathinput'] = 'manual'
        params['username'] = 'user2'
        params['reposname'] = 'repos1'
        params['pathname'] = '/trunk/src/test'
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[repos1:/trunk/src/test] user2 = r</div>''' in res.body, res.body

        params['userinput'] = 'select'
        params['reposinput'] = 'select'
        params['pathinput'] = 'manual'
        params['userselector'] = 'user2'
        params['reposselector'] = 'reposX'
        params['pathname'] = '/trunk/'
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[reposX:/trunk] user2 =</div>''' in res.body, res.body

        params['userinput'] = 'select'
        params['reposinput'] = 'select'
        params['pathinput'] = 'select'
        params['userselector'] = 'user3'
        params['reposselector'] = 'repos1'
        params['pathselector'] = '/trunk'
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[repos1:/trunk] user3 =</div>''' in res.body, res.body

        params['userselector'] = 'user4'
        params['reposselector'] = 'repos1'
        params['pathselector'] = '/trunk'
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[repos1:/trunk] user4 = r</div>''' in res.body, res.body

        params['userselector'] = 'user4'
        params['reposselector'] = 'reposX'
        params['pathselector'] = '/trunk'
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[reposX:/trunk] user4 = r</div>''' in res.body, res.body

        params['userselector'] = 'user5'
        params['reposselector'] = 'reposX'
        params['pathselector'] = '/trunk'
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[reposX:/trunk] user5 =</div>''' in res.body, res.body


    def test_authz_path(self):
        # authn test
        res = self.app.get(url_for(controller='check', action='get_auth_path'))
        assert res.status == 302
        self.assertEqual(res.header('location'), '/security')

        # authz test
        self.login('nobody')
        res = self.app.get(url_for(controller='check', action='get_auth_path'))
        assert res.status == 200, res.status
        self.assert_('Permission denied.' in res.body, res.body)

        self.login('root')
        params = {}
        params['repos'] = '/'
        res = self.app.get(url_for(controller='check', action='get_auth_path'), params)
        assert res.status == 200
        assert '''id[0]="...";name[0]="Please choose...";
id[1]="/trunk/src";name[1]="/trunk/src";
id[2]="/trunk";name[2]="/trunk";
id[3]="/";name[3]="/";
id[4]="/tags";name[4]="/tags";
id[5]="/branches";name[5]="/branches";
total=6;
''' == res.body, res.body

        params['repos'] = 'noexist'
        res = self.app.get(url_for(controller='check', action='get_auth_path'), params)
        assert res.status == 200
        assert '' == res.body, res.body

        params['repos'] = 'repos1'
        res = self.app.get(url_for(controller='check', action='get_auth_path'), params)
        assert res.status == 200
        assert '''id[0]="...";name[0]="Please choose...";
id[1]="/trunk/src";name[1]="/trunk/src";
id[2]="/trunk";name[2]="/trunk";
id[3]="/";name[3]="/";
total=4;
''' == res.body, res.body

        params['repos'] = 'document'
        res = self.app.get(url_for(controller='check', action='get_auth_path'), params)
        assert res.status == 200
        assert u'''id[0]="...";name[0]="Please choose...";
id[1]="/branches";name[1]="/branches";
id[2]="/tags";name[2]="/tags";
id[3]="/trunk/.htgroup";name[3]="/trunk/.htgroup";
id[4]="/trunk/tech";name[4]="/trunk/tech";
id[5]="/trunk/tech/.htaccess";name[5]="/trunk/tech/.htaccess";
id[6]="/trunk/商务部";name[6]="/trunk/商务部";
id[7]="/trunk/商务部/.htaccess";name[7]="/trunk/商务部/.htaccess";
id[8]="/trunk/行政部";name[8]="/trunk/行政部";
id[9]="/trunk/行政部/.htaccess";name[9]="/trunk/行政部/.htaccess";
total=10;
''' == unicode(res.body, 'utf-8'), res.body
