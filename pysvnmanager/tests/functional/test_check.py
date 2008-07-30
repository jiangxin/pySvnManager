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
        assert res.status == 302, res.status
        assert res.header('location')== '/security/failed', res.header('location')
        
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
        assert res.status == 302, res.status
        assert res.header('location')== '/security/failed', res.header('location')
        
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

        params = {
                  'userinput':'select', 
                  'reposinput':'select', 
                  'pathinput':'select',
                  'userselector':'user1',
                  'reposselector':'reposX',
                  'pathselector':'/trunk/src/test',
                  'abbr':'False',
                  }
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>User user1 has ReadOnly (RO) rights for module reposX:/trunk/src/test</div><pre>
==================================================
Access map on 'reposX' for user 'user1'
==================================================
  * Writable:
    
----------------------------------------
  * Readable:
    /branches
    /tags
    /trunk/src
----------------------------------------
  * Denied:
    /
    /trunk
----------------------------------------
''' in res.body, res.body

        params = {
                  'userinput':'manual', 
                  'reposinput':'manual', 
                  'pathinput':'manual',
                  'username':'user2',
                  'reposname':'repos1',
                  'pathname':'/trunk/src/test',
                  'abbr':'1',
                  }
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[repos1:/trunk/src/test] user2 = r</div>''' in res.body, res.body

        params = {
                  'userinput':'select', 
                  'reposinput':'select', 
                  'pathinput':'manual',
                  'userselector':'user2',
                  'reposselector':'reposX',
                  'pathname':'/trunk/',
                  'abbr':'1',
                  }
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[reposX:/trunk] user2 =</div>''' in res.body, res.body

        params = {
                  'userinput':'select', 
                  'reposinput':'select', 
                  'pathinput':'select',
                  'userselector':'user3',
                  'reposselector':'repos1',
                  'pathselector':'/trunk',
                  'abbr':'1',
                  }
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[repos1:/trunk] user3 =</div>''' in res.body, res.body

        params = {
                  'userinput':'select', 
                  'reposinput':'select', 
                  'pathinput':'select',
                  'userselector':'user4',
                  'reposselector':'repos1',
                  'pathselector':'/trunk',
                  'abbr':'1',
                  }
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[repos1:/trunk] user4 = r</div>''' in res.body, res.body

        params = {
                  'userinput':'select', 
                  'reposinput':'select', 
                  'pathinput':'select',
                  'userselector':'user4',
                  'reposselector':'reposX',
                  'pathselector':'/trunk',
                  'abbr':'1',
                  }
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[reposX:/trunk] user4 = r</div>''' in res.body, res.body

        params = {
                  'userinput':'select', 
                  'reposinput':'select', 
                  'pathinput':'select',
                  'userselector':'user5',
                  'reposselector':'reposX',
                  'pathselector':'/trunk',
                  'abbr':'1',
                  }
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert '''<div id='acl_path_msg'>[reposX:/trunk] user5 =</div>''' in res.body, res.body

        # Repos = *
        self.login('admin2')
        params = {
                  'userinput':'select', 
                  'userselector':'user1',
                  'reposinput':'select', 
                  'reposselector':'*',
                  'pathinput':'select',
                  'pathselector':'/trunk/src/test',
                  'abbr':'True',
                  }
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert res.status == 200, res.status
        assert '''<div id='acl_path_msg'>[repos1:/trunk/src/test] user1 =<br>
[repos2:/trunk/src/test] user1 = r</div><pre>
user1 => [repos1]
----------------------------------------
RW: 
RO: /branches, /tags, /trunk
XX: /, /trunk/src



user1 => [repos2]
----------------------------------------
RW: /, /trunk
RO: /branches, /tags, /trunk/src
XX: 

</pre>''' in res.body, repr(res.body)

        # permision deny test
        self.login('admin2')
        params = {
                  'userinput':'select', 
                  'reposinput':'select', 
                  'pathinput':'select',
                  'userselector':'user1',
                  'reposselector':'repos3',
                  'pathselector':'/trunk/src/test',
                  'abbr':'True',
                  }
        res = self.app.get(url_for(controller='check', action='access_map'), params)
        assert res.status == 200, res.status
        assert res.body== 'Permission denied.', res.header('location')

    def test_authz_path(self):
        # authn test
        res = self.app.get(url_for(controller='check', action='get_auth_path'))
        assert res.status == 302
        assert res.header('location')== '/security', res.header('location')

        # authz test
        self.login('nobody')
        res = self.app.get(url_for(controller='check', action='get_auth_path'))
        assert res.status == 302, res.status
        assert res.header('location')== '/security/failed', res.header('location')

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
