## -*- coding: utf-8 -*-

from pysvnmanager.tests import *
from pylons import config

class TestLoginController(TestController):

    def test_login_logout(self):
        params={}
        # login successful
        params['username'] = 'root'
        d = eval(config.get('test_users', {}))
        password = d.get(params['username'],'')
        params['password'] = password
        res = self.app.get(url_for(controller='security', action='submit'), params)
        self.assert_(res.status == 302)
        self.assert_(res.all_headers('location') == ['/check'])
        self.assert_(res.session['user'] == 'root', res.session)
        
        # keep session test
        res = self.app.get(url_for(controller='security', action='index'))
        self.assert_('<h2>Login</h2>' in res.body, res.body)
        self.assert_(res.session['user'] == 'root', res.session)
                                   
        # login with wrong password
        params['username'] = 'root'
        params['password'] = 'wrong_passwd'
        res = self.app.get(url_for(controller='security', action='submit'), params)
        self.assert_(res.status == 200, res.status)
        self.assert_('Login failed for user: root' in res.body, res.body)
        self.assert_(res.session.get('user') == None, res.session.get('user'))
        
        self.login('jiangxin')
        res = self.app.get(url_for(controller='security', action='index'))
        self.assert_(res.session.get('user') == 'jiangxin', res.session)

        # logout
        res = self.app.get(url_for(controller='security', action='logout'))
        self.assert_(res.status == 302)
        self.assert_(res.all_headers('location') == ['/security'])
        self.assert_(res.session.get('user') == None, res.session.get('user'))
