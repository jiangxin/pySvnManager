#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import sys
#sys.path.insert(0,'/home/jiangxin/codebase/python/svnauthz');
#sys.path.insert(0,'..');
#sys.path.insert(0,'../svnauthz');

#import unittest
#from svnauthz.svnauthz import *
#import StringIO
#from pprint import pprint

from pysvnmanager.tests import *
from pysvnmanager import model
from pysvnmanager.model.svnauthz import *
import StringIO
from pprint import pprint

class TestModels(TestController):
    def __init__(self, *args):
        self.authz = self.load_config()
        super(TestModels, self).__init__(*args)

    def load_config(self, init=True):

        buff = '''
# version = 0.1.1
# admin : / = root, &admin
# admin : repos1 = @admin
# admin : repos2 = admin2
# admin : repos3 = admin3
# admin : reposx = 

[groups]
admins=&admin,&007
admin=&admin, admin1, admin2, admin3
team1=user1,user11, @team2
team2=user2,user22,@team3,
# Wrong configuration: cyclic dependancies
#   team1->team2->team3->team1->...
# We can detect and fix.
team3=user3,user33,@team1
all=@team1,user3,user4

[aliases]
admin=jiangxin
007=james


[repos1:/trunk/src]
user1=
&007 = r

[/trunk/src]
user1=r
user2=r

[repos1:/trunk]
user1=r
user2=

[/trunk]
user2=

[repos1:/]
user3=
@admins=rw

[/]
user3=r
user4=r

[/branches]
$authenticated = r
@admins = rw

[/tags]
* = 
@all = r
@admins = rw
        '''

        if init:
            file = StringIO.StringIO(buff)
            self.authz = SvnAuthz(file)
        else:
            self.authz = SvnAuthz()

    def testAlias(self):
        alist = AliasList()
        self.assert_(list(alist) == [])
        a1 = alist.get_or_set('admin')
        user = User('jiangxin')
        a1.user = user
        self.assert_(str(a1) == 'admin = jiangxin', str(a1))

    def testGroup(self):
        user1 = User('user1')
        user2 = User('user2')
        team = Group('team2')
        alias = Alias('admin')

        g = Group('team1')
        self.assert_(g.name == 'team1')
        self.assert_(g.uname == '@team1')
        g.append([user1, user2])
        self.assert_(g.membernames == ['user1','user2'], g.membernames)

        g.append([team, alias])
        self.assert_(g.membernames == ['user1', 'user2', '@team2', '&admin'], g.membernames)
        self.assert_(str(g) == 'team1 = &admin, @team2, user1, user2', str(g))

    def testUserList(self):
        ul = UserList()
        self.assert_(list(ul) == [])
        user1 = ul.get_or_set('jiangxin')
        self.assert_(user1.name == 'jiangxin')
        self.assert_(user1.uname == 'jiangxin')
        self.assert_(list(ul) == [user1])
        user2 = ul.get_or_set('user2')
        self.assert_(user2.name == 'user2')
        self.assert_(user2.uname == 'user2')
        self.assert_(list(ul) == [user1, user2])

    def testAliasList(self):
        alist = AliasList()
        self.assert_(list(alist) == [])
        alias1 = alist.get_or_set('admin')
        self.assert_(alias1.name == 'admin')
        self.assert_(alias1.uname == '&admin')
        self.assert_(list(alist) == [alias1])
        alias2 = alist.get_or_set('root')
        self.assert_(alias2.name == 'root')
        self.assert_(alias2.uname == '&root')
        self.assert_(list(alist)== [alias1, alias2])

    def testGroupList(self):
        gl = GroupList()
        self.assert_(list(gl) == [])
        g1 = gl.get_or_set('team1')
        self.assert_(g1.name == 'team1')
        self.assert_(g1.uname == '@team1')
        self.assert_(list(gl) == [g1])
        g2 = gl.get_or_set('team2')
        self.assert_(g2.name == 'team2')
        self.assert_(g2.uname == '@team2')
        self.assert_(list(gl) == [g1, g2])

    def testRules(self):
        pass

    def testModule(self):
        module = Module('/', '/trunk')
        self.assert_(module.path == '/trunk')
        obj = Group('* ')
        module.update_rule(obj,'')
        obj = Group('admins')
        module.update_rule(obj, 'rw')
        obj = Group('* ')
        module.update_rule(obj, 'r')
        obj = User(' jiang ')
        module.update_rule(obj, '')
        obj = Group(' $authenticated ')
        module.update_rule(obj, 'r')
        self.assert_(str(module) == 
'''[/trunk]
$authenticated = r
* = r
@admins = rw
jiang = 
''', repr(str(module)))

        module = Module('myrepos', '')
        obj = Group('* ')
        module.update_rule(obj,'r')
        obj = Group(' team1 ')
        module.update_rule(obj,'rw')
        obj = Group('*')
        module.update_rule(obj,'')
        obj = User(' jiang ')
        module.update_rule(obj,'')
        obj = Group('$authenticated')
        module.update_rule(obj,'r')
        self.assert_(str(module) == '''[myrepos:/]
$authenticated = r
* = 
@team1 = rw
jiang = 
''', repr(str(module)))
        pass

    def testReposAdmin(self):
        authz = SvnAuthz()
        u1=authz.add_user('u1')
        u2=authz.add_user('u2')
        u3=authz.add_user('u3')
        u4=authz.add_user('u4')
        u5=authz.add_user('u5')
        u6=authz.add_user('u6')
        u7=authz.add_user('u7')
        admin = authz.add_alias('admin', 'u1')
        team1 = authz.add_group('team1', 'u2, u3, u4')
        repos1 = authz.add_repos('repos1')
        
        authz.set_admin('&admin, u7')
        authz.set_admin('@team1', 'repos1')
        self.assert_(authz.get_repos('/').admins == '&admin, u7')
        self.assert_(authz.get_repos('/repos1').admins == '@team1')
        authz.set_admin(', @team1, ', 'repos1')
        self.assert_(authz.get_repos('repos1').admins == '@team1')
        authz.set_admin(['&admin', 'u6'])
        self.assert_(authz.get_repos('/').admins == '&admin, u6')
        authz.set_admin([admin, u5])
        self.assert_(authz.get_repos('/').admins == '&admin, u5')

        authz.set_admin('')
        self.assert_(authz.get_repos('/').admins == '')
        authz.set_admin([])
        self.assert_(authz.get_repos('/').admins == '')
        authz.set_admin(None)
        self.assert_(authz.get_repos('/').admins == '')

    def testAuthzConfAcl(self):
        if not self.authz: self.load_config()
        rl = self.authz.reposlist
        self.assert_(rl.get('/').name == '/')
        self.assert_(rl.get('/').admins == '&admin, root', rl.get('/').admins)
        self.assert_(rl.get('repos1').name == 'repos1')
        self.assert_(rl.get('repos1').admins == '@admin', rl.get('repos1').admins)
        self.assert_(rl.get('repos2').name == 'repos2', 'name: %s' % rl.get('repos2').name)
        self.assert_(rl.get('repos2').admins == 'admin2', rl.get('repos2').admins)
        self.assert_(self.authz.compose_acl() == 
'''# admin : / = &admin, root
# admin : repos1 = @admin
# admin : repos2 = admin2
# admin : repos3 = admin3
''', self.authz.compose_acl())
        pass

    def testAuthzConfAliases(self):
        if not self.authz: self.load_config()
        al = self.authz.aliaslist
        self.assert_(al.get('admin').username == 'jiangxin', str(al.get('admin')))
        self.assert_(str(al) == '[aliases]\n007 = james\nadmin = jiangxin\n', repr(str(al)))
        pass

    def testAuthzConfGroups(self):
        if not self.authz: self.load_config()
        gl = self.authz.grouplist
        self.assert_(sorted(gl.get('admins').membernames) == ['&007', '&admin'],
                     sorted(gl.get('admins').membernames))
        self.assert_(sorted(gl.get('team1').membernames) == 
                     ['@team2', 'user1', 'user11'],
                     sorted(gl.get('team1').membernames))
        self.assert_(sorted(gl.get('all').membernames) == 
                     ['@team1', 'user3', 'user4'],
                     sorted(gl.get('all').membernames))
        self.assert_(str(gl) == 
            '''[groups]
admin = &admin, admin1, admin2, admin3
admins = &007, &admin
all = @team1, user3, user4
team1 = @team2, user1, user11
team2 = @team3, user2, user22
team3 = user3, user33
''', repr(str(gl)))
        pass

    def testAuthzConfRepos(self):
        # blank configuration
        self.load_config(init=False)
        # add_repos
        self.assert_(isinstance(self.authz.add_repos('repos1'), Repos))
        self.assert_(isinstance(self.authz.add_repos('repos2'), Repos))
        self.assert_(','.join(map(lambda x:x.name, self.authz.reposlist)) ==
                     '/,repos1,repos2', ','.join(map(lambda x:x.name,
                                                     self.authz.reposlist)))
        # add_admin
        self.assert_(self.authz.set_admin('admin1,admin2') == True)
        self.assert_(self.authz.is_admin('admin1','/') == True)
        self.assert_(self.authz.set_admin('adminx', 'repos1') == True)
        self.assert_(self.authz.is_admin('adminx', 'repos1') == True)
        self.assert_(self.authz.is_super_user('admin1') == True)
        self.assert_(self.authz.is_super_user('adminx') == False)

        self.assert_(self.authz.get_manageable_repos_list('admin1') == ['/', 'repos1', 'repos2'], self.authz.get_manageable_repos_list('admin1'))
        self.assert_(self.authz.get_manageable_repos_list('adminx') == ['repos1'], self.authz.get_manageable_repos_list('adminx'))
        self.assert_(self.authz.get_manageable_repos_list('adminxyz') == [])
        self.assert_(self.authz.get_manageable_repos_list('') == [])
        # add_module (repos = /)
        self.assert_(isinstance(self.authz.add_module('/', '/trunk///'), Module))
        m = self.authz.get_module('/', '/trunk/')
        self.assert_(isinstance(m, Module))
        self.assert_(m.path == '/trunk')
        self.assert_(m.repos == '/')
        # add_module (path = /)
        self.assert_(isinstance(self.authz.add_module('repos1', '/'), Module))
        m = self.authz.get_module('repos1', '')
        self.assert_(m.repos+':'+m.path == 'repos1:/')
        self.assert_(','.join(map(lambda x:x.repos+':'+x.path,
                                  self.authz.modulelist())) ==
                     '/:/trunk,repos1:/', ','.join(map(lambda
                                                       x:x.repos+':'+x.path,
                                                       self.authz.modulelist())))

        # add_alias
        user = self.authz.add_user('jiangxin')
        self.assert_(isinstance(self.authz.add_alias('superuser', user), Alias))
        self.assert_(isinstance(self.authz.add_alias('root', user), Alias))
        self.assert_(str(self.authz.aliaslist) == '[aliases]\nroot = jiangxin\nsuperuser = jiangxin\n', repr(str(self.authz.aliaslist)))
        self.assert_(','.join(map(lambda x:x.name, self.authz.aliaslist)) ==
                     'superuser,root', ','.join(map(lambda x:x.name,
                                                    self.authz.aliaslist)))

        # add_group
        self.assert_(str(self.authz.grouplist) == '[groups]\n', repr(str(self.authz.grouplist)))
        self.assert_(isinstance(self.authz.add_group('myteam','user1'), Group))
        self.assert_(str(self.authz.grouplist) == '[groups]\nmyteam = user1\n', repr(str(self.authz.grouplist)))
        self.assert_(isinstance(self.authz.add_group_member('myteam','user2,user3'), Group))
        self.assert_(isinstance(self.authz.add_group_member('myteam','user2,user3'), Group))
        self.assert_(str(self.authz.grouplist) == '[groups]\nmyteam = user1, user2, user3\n', repr(str(self.authz.grouplist)))
        self.assert_(','.join(map(lambda x:x.name, self.authz.grouplist)) ==
                     'myteam', ','.join(map(lambda x:x.name,
                                            self.authz.grouplist)))
        self.assert_(isinstance(self.authz.add_group_member('team1','@team2'),Group))
        self.assert_(isinstance(self.authz.add_group_member('myteam','@team1, @team2, *, $authenticated'),Group))
        self.assert_(isinstance(self.authz.add_group_member('team2','$authenticated,*'),Group))
        self.assert_(isinstance(self.authz.add_group_member('team3','@team4'),Group))
        self.assert_(isinstance(self.authz.add_group_member('team4','@myteam'),Group))
        self.assertRaises(Exception, self.authz.add_group_member, 'myteam','@team3, @team4, @team5')
        self.assert_(str(self.authz.grouplist.get('@myteam')) == 
                     'myteam = $authenticated, *, @team1, @team2, user1, user2, user3', 
                     repr(str(self.authz.grouplist.get('@myteam')))) 
        self.assert_(isinstance(self.authz.add_group_member('myteam','@team3, @team4, @team5', True),Group))
        self.assert_(str(self.authz.grouplist.get('@myteam')) == 
                     'myteam = $authenticated, *, @team1, @team2, @team5, user1, user2, user3', 
                     repr(str(self.authz.grouplist.get('@myteam')))) 
        self.assertRaises(Exception, self.authz.del_group, '@team2')
        self.assert_(str(self.authz.grouplist.get('@team2')) == 'team2 = $authenticated, *', 
                     self.authz.grouplist.get('@team2'))
        self.assert_(self.authz.del_group('@team2',force=True)==True)
        self.assert_(self.authz.grouplist.get('@team2') == None, 
                     str(self.authz.grouplist.get('@team2')))
        self.assert_(str(self.authz.grouplist.get('@myteam')) == 
                     'myteam = $authenticated, *, @team1, @team5, user1, user2, user3',
                     repr(str(self.authz.grouplist.get('@myteam')))) 
        self.assert_(str(self.authz.grouplist.get('@team1')) == 'team1 = ',
                     repr(str(self.authz.grouplist.get('@team1')))) 

        # add_rule 
        module = self.authz.get_module('/', '/trunk/')
        tmpstr = "%s" % module
        self.assert_(tmpstr =='', tmpstr)
        self.authz.set_rules('/', '/trunk', 'user1=r\nuser1 = rw\n user2 =\n')
        tmpstr = "%s" % module
        self.assert_(tmpstr ==u'[/trunk]\nuser1 = rw\nuser2 = \n', repr(tmpstr))
        self.authz.set_rules('/', '/trunk', '')
        tmpstr = "%s" % module
        self.assert_(tmpstr ==u'', repr(tmpstr))

        self.assert_(self.authz.add_rules('/', '/trunk/', '&superuser=rw') == True, self.authz.add_rules('/', '/trunk/', '&superuser=rw'))
        self.assert_(self.authz.add_rules('repos1', '/', '*=r') == True, self.authz.add_rules('repos1', '/', '*=r'))
        self.assert_(str(self.authz.get_module('repos1', '/')) == '[repos1:/]\n* = r\n', repr(str(self.authz.get_module('repos1', '/'))))
        self.assert_(self.authz.add_rules('repos1', '/', ['*=', '@team1=rw']) == True)
        self.assert_(str(self.authz.get_module('repos1', '/')) == '[repos1:/]\n* = \n@team1 = rw\n', repr(str(self.authz.get_module('repos1', '/'))))
        self.assert_(','.join(map(lambda x:str(x), self.authz.rulelist())) ==
                     '&superuser = rw,* = ,@team1 = rw', ','.join(map(lambda
                                                                      x:str(x),
                                                                      self.authz.rulelist())))
        self.assertRaises(Exception, self.authz.chk_grp_ref_by_rules, '*')
        self.assertRaises(Exception, self.authz.chk_grp_ref_by_rules, '@team1')
        self.authz.chk_grp_ref_by_rules('@team2')

        self.assert_(self.authz.del_rule('repos1', '/', ['*=rw']) == True)
        self.assert_(str(self.authz.get_module('repos1', '/')) == '[repos1:/]\n@team1 = rw\n', repr(str(self.authz.get_module('repos1', '/'))))
        self.assert_(','.join(map(lambda x:x.name, self.authz.grouplist)) ==
                     'myteam,team1,*,$authenticated,team3,team4,team5',
                     ','.join(map(lambda x:x.name, self.authz.grouplist)))

        # del_alias
        self.authz.chk_alias_ref_by_rules('&root')
        self.assert_(self.authz.del_alias('&root') == True)
        self.assertRaises(Exception, self.authz.chk_alias_ref_by_rules, '&superuser')
        self.assertRaises(Exception, self.authz.del_alias, '&superuser')
        self.assert_(','.join(map(lambda x:x.name, self.authz.aliaslist)) ==
                     'superuser', ','.join(map(lambda x:x.name,
                                               self.authz.aliaslist)))

        # del_group
        self.assertRaises(Exception, self.authz.chk_grp_ref_by_rules,'@team1')
        self.assertRaises(Exception, self.authz.del_group,'@team1')
        self.authz.chk_grp_ref_by_rules('myteam')
        self.assertRaises(Exception, self.authz.del_group,'@myteam')
        self.assert_(','.join(map(lambda x:x.name, self.authz.grouplist)) ==
                     'myteam,team1,*,$authenticated,team3,team4,team5',
                     ','.join(map(lambda x:x.name, self.authz.grouplist)))
        self.assert_(self.authz.del_group('@myteam',force=True) == True)
        self.assert_(','.join(map(lambda x:x.name, self.authz.grouplist)) ==
                     'team1,*,$authenticated,team3,team4,team5',
                     ','.join(map(lambda x:x.name, self.authz.grouplist)))

        # remove
        self.assert_(isinstance(self.authz.add_group_member('myteam','user1,user2,user3'),Group))
        self.assert_(self.authz.del_group_member('myteam','user1,user3') == True)
        self.assert_(str(self.authz.grouplist) == 
                     '[groups]\nmyteam = user2\nteam1 = \nteam3 = @team4\nteam4 = \nteam5 = \n',
                     repr(str(self.authz.grouplist)))

        # del_module
        self.assert_(self.authz.del_module('repos2', '/') == False)
        self.assert_(self.authz.del_module('repos1', '/') == True)
        self.assert_(self.authz.get_module('repos1', '/') == None)

        # del_repos
        #self.assert_(str(self.authz) == '', str(self.authz))
        self.assert_(self.authz.get_repos('/').is_blank() == False)
        self.assert_(self.authz.get_repos('repos2').is_blank() == True)
        self.assert_(self.authz.get_repos('repos1').is_blank() == False)
        self.assert_(self.authz.del_repos('/') == False)
        self.assert_(self.authz.del_repos('/', recursive=True) == True)
        self.assert_(self.authz.get_repos('/').is_blank() == False)
        self.assert_(self.authz.del_repos('repos2') == True)
        self.assert_(self.authz.del_repos('repos1') == False)
        self.assert_(self.authz.del_repos('repos1',recursive=True) == True)

        # output config from __str__
        self.assert_(str(self.authz) == 
                     '# version : 0.1.0\n# admin : / = admin1, admin2\n\n[groups]\nmyteam = user2\nteam1 = \nteam3 = @team4\nteam4 = \nteam5 = \n\n[aliases]\nsuperuser = jiangxin\n\n', 
                     repr(str(self.authz)))


        ###########################################################
        # Load Built-in svnauthz config
        self.load_config(init=True)
        # is_admin()
        self.assert_(self.authz.is_admin('jiangxin') == True)
        self.assert_(self.authz.is_admin('root') == True, self.authz.is_admin('root'))
        self.assert_(self.authz.is_super_user('jiangxin') == True)
        self.assert_(self.authz.is_admin('&admin') == True)
        self.assert_(self.authz.is_admin('admin1') == False)
        self.assert_(self.authz.is_admin('admin1','repos1') == True)
        self.assert_(self.authz.is_admin('admin4','repos1') == False)
        self.assert_(self.authz.is_admin('admin1','repos2') == False)
        self.assert_(self.authz.is_admin('admin2','repos2') == True)
        self.assert_(self.authz.is_admin('admin10','repos2') == False)
        self.assert_(self.authz.is_admin('','repos3') == False)
        self.assert_(self.authz.is_admin('jiangxin','repos123') == True)

        # add_admin() test
        self.assert_(self.authz.set_admin('admin1,admin2') == True)
        self.assert_(self.authz.set_admin(['admin1','admin2'],'repos1') == True)
        # reposx does not exist.
        self.assert_(self.authz.set_admin('admin2','reposx') == False)
        self.assert_(self.authz.is_admin('admin1','repos2') == True)


        # SvnAuthz __str__ test
        self.authz.update_revision()
        self.assert_(str(self.authz) ==
"""# version : 0.1.2
# admin : / = admin1, admin2
# admin : repos1 = admin1, admin2
# admin : repos2 = admin2
# admin : repos3 = admin3

[groups]
admin = &admin, admin1, admin2, admin3
admins = &007, &admin
all = @team1, user3, user4
team1 = @team2, user1, user11
team2 = @team3, user2, user22
team3 = user3, user33

[aliases]
007 = james
admin = jiangxin

[/]
user3 = r
user4 = r

[/branches]
$authenticated = r
@admins = rw

[/tags]
* = 
@admins = rw
@all = r

[/trunk]\nuser2 = 

[/trunk/src]
user1 = r
user2 = r

[repos1:/]
@admins = rw
user3 = 

[repos1:/trunk]
user1 = r
user2 = 

[repos1:/trunk/src]
&007 = r
user1 = 

""", (repr(str(self.authz))))

        self.assert_(self.authz.check_rights('user1','repos1','/trunk/src/test','r') == False)
        self.assert_(self.authz.check_rights('user1','GLOBAL','/trunk/src/test','r') == True)
        self.assert_(self.authz.check_rights('user2','repos1','/trunk/src/test','r') == True)
        self.assert_(self.authz.check_rights('user2','repos1','/trunk','r') == False)
        self.assert_(self.authz.check_rights('user2','GLOBAL','/trunk','r') == False)
        self.assert_(self.authz.check_rights('user3','repos1','/trunk','r') == False)
        self.assert_(self.authz.check_rights('user4','repos1','/trunk','r') == True)
        self.assert_(self.authz.check_rights('user4','GLOBAL','/trunk','r') == True)
        self.assert_(self.authz.check_rights('user5','GLOBAL','/trunk','r') == False, self.authz.check_rights('user5','GLOBAL','/trunk','r'))

        self.assert_(self.authz.check_rights('user5','GLOBAL','/branches/a/b/c','r') == True)

        self.assert_(self.authz.get_access_map_msgs('jiangxin', 'repos2') == 
["""
==================================================
Access map on 'repos2' for user 'jiangxin'
==================================================
  * Writable:
    /branches
    /tags
----------------------------------------
  * Readable:
    
----------------------------------------
  * Denied:
    /
    /trunk
    /trunk/src
----------------------------------------
"""], repr(self.authz.get_access_map_msgs('jiangxin', 'repos2')))


if __name__ == '__main__': unittest.main()

