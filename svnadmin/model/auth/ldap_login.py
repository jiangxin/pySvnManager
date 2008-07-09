# -*- coding: utf-8 -*-
import logging
import sys
import ldap
log = logging.getLogger(__name__)

def ldap_login(username, password, config):
    """ get authentication data from form, authenticate against LDAP (or Active
        Directory), fetch some user infos from LDAP and create a user object
        for that user. The session is kept by the moin_session auth plugin.
    """
    verbose = getattr(config, 'ldap_verbose', False)

    # we require non-empty password as ldap bind does a anon (not password
    # protected) bind if the password is empty and SUCCEEDS!
    if not password or not username or not config:
        return False

    try:
        try:
            u = None
            dn = None
            coding = getattr(config, 'ldap_coding', 'utf-8')
            log.debug("LDAP: Setting misc. options...")
            ldap.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3) # ldap v2 is outdated
            ldap.set_option(ldap.OPT_REFERRALS, getattr(config, 'ldap_referrals', 0))
            ldap.set_option(ldap.OPT_NETWORK_TIMEOUT, getattr(config, 'ldap_timeout',10))

            starttls = getattr(config, 'ldap_start_tls', False)
            if hasattr(ldap, 'TLS_AVAIL') and ldap.TLS_AVAIL:
                for option, value in (
                    (ldap.OPT_X_TLS_CACERTDIR, getattr(config, 'ldap_tls_cacertdir', '')),
                    (ldap.OPT_X_TLS_CACERTFILE, getattr(config, 'ldap_tls_cacertfile', '')),
                    (ldap.OPT_X_TLS_CERTFILE, getattr(config, 'ldap_tls_certfile', '')),
                    (ldap.OPT_X_TLS_KEYFILE, getattr(config, 'ldap_tls_keyfile', '')),
                    (ldap.OPT_X_TLS_REQUIRE_CERT, getattr(config, 'ldap_tls_require_cert', ldap.OPT_X_TLS_NEVER)),
                    (ldap.OPT_X_TLS, starttls),
                    #(ldap.OPT_X_TLS_ALLOW, 1),
                ):
                    if value:
                        ldap.set_option(option, value)

            server = getattr(config, 'ldap_uri', 'ldap://localhost')
            if verbose: log.debug("LDAP: Trying to initialize %r." % server)
            l = ldap.initialize(server)
            if verbose: log.debug("LDAP: Connected to LDAP server %r." % server)

            if starttls and server.startswith('ldap:'):
                if verbose: log.debug("LDAP: Trying to start TLS to %r." % server)
                try:
                    l.start_tls_s()
                    if verbose: log.debug("LDAP: Using TLS to %r." % server)
                except (ldap.SERVER_DOWN, ldap.CONNECT_ERROR), err:
                    if verbose: log.debug("LDAP: Couldn't establish TLS to %r (err: %s)." % (server, str(err)))
                    raise

            # you can use %(username)s and %(password)s here to get the stuff entered in the form:
            ldap_binddn = getattr(config, 'ldap_binddn', '') % locals()
            ldap_bindpw = getattr(config, 'ldap_bindpw', '') % locals()
            l.simple_bind_s(ldap_binddn.encode(coding), ldap_bindpw.encode(coding))
            if verbose: log.debug("LDAP: Bound with binddn %r" % ldap_binddn)

            # you can use %(username)s here to get the stuff entered in the form:
            filterstr = getattr(config, 'ldap_filter', '(&(uid=%(username)s)(authorizedService=svn)(ossxpConfirmed=TRUE))') % locals()

            #attrs = [getattr(config, attr) for attr in [
            #                         'ldap_email_attribute',
            #                         'ldap_aliasname_attribute',
            #                         'ldap_surname_attribute',
            #                         'ldap_givenname_attribute',
            #                         ] if getattr(config, attr) is not None]
            attrs = ['cn', 'sn']

            if verbose: log.debug("LDAP: Searching %r" % filterstr)
            lusers = l.search_st(config.ldap_base, getattr(config, 'ldap_scope', ldap.SCOPE_SUBTREE), filterstr.encode(coding),
                                 attrlist=attrs, timeout=getattr(config, 'ldap_timeout', 10))
            # we remove entries with dn == None to get the real result list:
            lusers = [(dn, ldap_dict) for dn, ldap_dict in lusers if dn is not None]
            if verbose:
                for dn, ldap_dict in lusers:
                    log.debug("LDAP: dn:%r" % dn)
                    for key, val in ldap_dict.items():
                        log.debug("    %r: %r" % (key, val))

            result_length = len(lusers)
            if result_length != 1:
                if result_length > 1:
                    log.debug("LDAP: Search found more than one (%d) matches for %r." % (result_length, filterstr))
                if result_length == 0:
                    if verbose: log.debug("LDAP: Search found no matches for %r." % (filterstr, ))
                return False # if ldap returns unusable results, we veto the user and don't let him in

            dn, ldap_dict = lusers[0]
            if verbose: log.debug("LDAP: DN found is %r, trying to bind with pw" % dn)
            l.simple_bind_s(dn, password.encode(coding))
            if verbose: log.debug("LDAP: Bound with dn %r (username: %r)" % (dn, username))


        except ldap.INVALID_CREDENTIALS, err:
            log.debug("LDAP: invalid credentials (wrong password?) for dn %r (username: %r)" % (dn, username))
            return False # if ldap says no, we veto the user and don't let him in

    except:
        import traceback
        info = sys.exc_info()
        log.debug("LDAP: caught an exception, traceback follows...")
        log.debug(''.join(traceback.format_exception(*info)))
        return False # something went completely wrong, in doubt we veto the login

    return True

