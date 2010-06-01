# -*- coding: utf-8 -*-

from pylons import config

class DefaultConfig:
    """ Default config values 
    Warning: do not change configuration here, change localconfig.py instead.
    Save localconfig.py.ini to the deploy directory as localconfig.py.
    """

    # authn_file: a .htpasswd style password file, used for pysvnmanager authentication.
    # You can change authn_file in <deploy>.ini file.

    # Unittest based on WebTest not initialized pylons.config
    if config.get('__file__') is None:
        import pylons.test
        wsgiapp = pylons.test.pylonsapp
        config = wsgiapp.config
    authn_file = config.get('authn_file', "") % {'here': config.get('here')}

    # authz_file: svn authz config file with administrative extension. (ossxp.com)
    # You can change authz_file in <deploy>.ini file.
    authz_file = config.get('authz_file', "") % {'here': config.get('here')}
    
    # Numbers of logs in each page.
    log_per_page = 10
    
    # svn repository root
    repos_root = config.get('repos_root', "") % {'here': config.get('here')}
    
    # pysvnmanager authentication method.
    # You can use htpasswd_login, or ldap_login, or both.
    # You can also implement your own auth module.
    #from pysvnmanager.model.auth.http import htpasswd_login
    #auth = [htpasswd_login, ] # single auth method

    # Htpasswd login parameters
    # Note: custom `authn_file' in your <deploy>.ini file

    #import ldap
    #from pysvnmanager.model.auth.ldap_login import ldap_login
    #auth = [ldap_login, htpasswd_login] # both
    #auth = [ldap_login] # ldap auth only
    
    # LDAP parameters
    ldap_uri = 'ldap://localhost'
    ldap_binddn = ''
    ldap_bindpw = ''
    ldap_base = 'dc=foo,dc=bar'
    ldap_scope = 2 # ldap.SCOPE_SUBTREE = 2
    ldap_filter = '(&(uid=%(username)s)(authorizedService=svn)(ossxpConfirmed=TRUE))'
    ldap_timeout = 10 # how long we wait for the ldap server [s]
    ldap_coding = 'utf-8' # coding used for ldap queries and result values
    ldap_start_tls = False
    
