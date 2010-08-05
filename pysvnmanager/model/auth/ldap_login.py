# -*- coding: utf-8 -*-

from pysvnmanager.model.ldap_api import LDAP

def ldap_login(username, password, config):
    """ get authentication data from form, authenticate against LDAP (or Active
        Directory), fetch some user infos from LDAP and create a user object
        for that user. The session is kept by the moin_session auth plugin.
    """
    # we require non-empty password as ldap bind does a anon (not password
    # protected) bind if the password is empty and SUCCEEDS!
    if not password or not username or not config:
        return False

    return LDAP(config).test_login(username, password)


# vim: et ts=4 sw=4
