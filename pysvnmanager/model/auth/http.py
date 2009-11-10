# -*- coding: utf-8 -*-

try:
    from crypt import crypt
except ImportError:
    # Native crypt is not supported by Windows, use fcrypt instead.
    from fcrypt import crypt

def htpasswd_login(username, password, config):
    authn_file = getattr(config, 'authn_file', '')
    if isinstance(username, str):
        username = unicode(username, 'utf-8')

    if authn_file:
        pwdfile = open(authn_file)
        for line in pwdfile:
            if line.strip().startswith('#') and ':' not in line:
                continue
            user, pwdhash = line.strip().split(':',1)
            if username == unicode(user,'utf-8'):
                if pwdhash == crypt(password, pwdhash[:2]):
                    return True
                break

    return False
