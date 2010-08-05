# -*- coding: utf-8 -*-

import ldap
import sys

import logging
log = logging.getLogger(__name__)


class LDAP(object):

    def __init__(self, config):
        self.config = config
        self.verbose = getattr(self.config, 'ldap_verbose', False)
        self.coding = getattr(self.config, 'ldap_coding', 'utf-8')
        self.l = self.ldap_bind()


    def ldap_bind(self):

        """ get authentication data from form, authenticate against LDAP (or Active
            Directory), fetch some user infos from LDAP and create a user object
            for that user. The session is kept by the moin_session auth plugin.
        """

        if not self.config or not hasattr(self.config, 'ldap_base'):
            log.warning("LDAP not config yet, must define ldap_base and other ldap settings.")
            return None

        try:
            u = None
            dn = None
            log.debug("LDAP: Setting misc. options...")
            ldap.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3) # ldap v2 is outdated
            ldap.set_option(ldap.OPT_REFERRALS, getattr(self.config, 'ldap_referrals', 0))
            ldap.set_option(ldap.OPT_NETWORK_TIMEOUT, getattr(self.config, 'ldap_timeout',10))

            starttls = getattr(self.config, 'ldap_start_tls', False)
            if hasattr(ldap, 'TLS_AVAIL') and ldap.TLS_AVAIL:
                for option, value in (
                    (ldap.OPT_X_TLS_CACERTDIR, getattr(self.config, 'ldap_tls_cacertdir', '')),
                    (ldap.OPT_X_TLS_CACERTFILE, getattr(self.config, 'ldap_tls_cacertfile', '')),
                    (ldap.OPT_X_TLS_CERTFILE, getattr(self.config, 'ldap_tls_certfile', '')),
                    (ldap.OPT_X_TLS_KEYFILE, getattr(self.config, 'ldap_tls_keyfile', '')),
                    (ldap.OPT_X_TLS_REQUIRE_CERT, getattr(self.config, 'ldap_tls_require_cert', ldap.OPT_X_TLS_NEVER)),
                    (ldap.OPT_X_TLS, starttls),
                    #(ldap.OPT_X_TLS_ALLOW, 1),
                ):
                    if value:
                        ldap.set_option(option, value)

            server = getattr(self.config, 'ldap_uri', 'ldap://localhost')
            if self.verbose: log.debug("LDAP: Trying to initialize %r." % server)
            l = ldap.initialize(server)
            if self.verbose: log.debug("LDAP: Connected to LDAP server %r." % server)

            if starttls and server.startswith('ldap:'):
                if self.verbose: log.debug("LDAP: Trying to start TLS to %r." % server)
                try:
                    l.start_tls_s()
                    if self.verbose: log.debug("LDAP: Using TLS to %r." % server)
                except (ldap.SERVER_DOWN, ldap.CONNECT_ERROR), err:
                    if self.verbose: log.debug("LDAP: Couldn't establish TLS to %r (err: %s)." % (server, str(err)))
                    raise

            # you can use %(username)s and %(password)s here to get the stuff entered in the form:
            ldap_binddn = getattr(self.config, 'ldap_binddn', '')
            ldap_bindpw = getattr(self.config, 'ldap_bindpw', '')
            l.simple_bind_s(ldap_binddn.encode(self.coding), ldap_bindpw.encode(self.coding))
            if self.verbose: log.debug("LDAP: Bound with binddn %r" % ldap_binddn)

        except ldap.INVALID_CREDENTIALS, err:
            log.debug("LDAP: invalid credentials (wrong password?) for dn %r (username: %r)" % (dn, username))
            return None # if ldap says no, we veto the user and don't let him in

        except:
            import traceback
            info = sys.exc_info()
            log.debug("LDAP: caught an exception, traceback follows...")
            log.debug(''.join(traceback.format_exception(*info)))
            return None # something went completely wrong, in doubt we veto the login
        else:
            return l


    def is_bind(self):
        return self.l is not None


    def fetch_user(self, username, attrs=None):
        if not self.is_bind():
            return None

        try:
            # you can use %(username)s here to get the stuff entered in the form:
            filterstr = getattr(self.config, 'ldap_filter', '(&(uid=%(username)s)(authorizedService=svn)(ossxpConfirmed=TRUE))') % { 'username': username }

            if attrs is None:
                attrs = [getattr(self.config, attr) for attr in [
                                         'ldap_uid_attribute',
                                         'ldap_email_attribute',
                                         'ldap_aliasname_attribute',
                                         'ldap_surname_attribute',
                                         'ldap_givenname_attribute',
                                         ] if getattr(self.config, attr) is not None]
            if self.verbose: log.debug("LDAP: Searching %r" % filterstr)
            lusers = self.l.search_st(self.config.ldap_base, getattr(self.config, 'ldap_scope', ldap.SCOPE_SUBTREE), filterstr.encode(self.coding),
                                 attrlist=attrs, timeout=getattr(self.config, 'ldap_timeout', 10))

            # we remove entries with dn == None to get the real result list:
            lusers = [(dn, ldap_dict) for dn, ldap_dict in lusers if dn is not None]
            if self.verbose:
                for dn, ldap_dict in lusers:
                    log.debug("LDAP: dn:%r" % dn)
                    for key, val in ldap_dict.items():
                        log.debug("    %r: %r" % (key, val))

        except ldap.INVALID_CREDENTIALS, err:
            log.debug("LDAP: invalid credentials (wrong password?) for dn %r (username: %r)" % (dn, username))
            return None # if ldap says no, we veto the user and don't let him in

        except:
            import traceback
            info = sys.exc_info()
            log.debug("LDAP: caught an exception, traceback follows...")
            log.debug(''.join(traceback.format_exception(*info)))
            return None # something went completely wrong, in doubt we veto the login
        else:
            return lusers


    def test_login(self, username, password):
        if not username or not password or self.l is None:
            return False

        lusers = self.fetch_user(username)


        result_length = len(lusers)
        if result_length != 1:
            if result_length > 1:
                log.debug("LDAP: Search found more than one (%d) matches for %r." % (result_length, filterstr))
            if result_length == 0:
                if self.verbose: log.debug("LDAP: Search found no matches for %r." % (filterstr, ))
            return False # if ldap returns unusable results, we veto the user and don't let him in

        dn, ldap_dict = lusers[0]
        if self.verbose: log.debug("LDAP: DN found is %r, trying to bind with pw" % dn)

        try:
            self.l.simple_bind_s(dn, password.encode(self.coding))

        except ldap.INVALID_CREDENTIALS, err:
            log.debug("LDAP: invalid credentials (wrong password?) for dn %r (username: %r)" % (dn, username))
            return False # if ldap says no, we veto the user and don't let him in

        except:
            import traceback
            info = sys.exc_info()
            log.debug("LDAP: caught an exception, traceback follows...")
            log.debug(''.join(traceback.format_exception(*info)))
            return False # something went completely wrong, in doubt we veto the login
        else:
            return True


 
# vim: et ts=4 sw=4
