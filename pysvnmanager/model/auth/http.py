# -*- coding: utf-8 -*-

from crypt import crypt

def htpasswd_login(username, password, config):
    authn_file = getattr(config, 'authn_file', '')
    try:
        if authn_file:
            pwdfile = open(authn_file)
            for line in pwdfile:
                user, pwdhash = line.strip().split(':',1)
                if username == user:
                    if pwdhash == crypt(password, pwdhash[:2]):
                        return True
                    break
    except:
        pass

    return False
