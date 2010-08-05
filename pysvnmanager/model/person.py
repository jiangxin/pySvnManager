# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 OpenSourceXpress Ltd. (http://www.ossxp.com)
# Author: Jiang Xin
# Contact: http://www.ossxp.com/
#          http://blog.ossxp.com/
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

"""Person model"""

from sqlalchemy import Column
from sqlalchemy.types import Integer, String

from pysvnmanager.model.meta import Session, Base
from pysvnmanager.model.ldap_api import LDAP

import logging
log = logging.getLogger(__name__)


class Person(Base):
    __tablename__ = "person"

    uid = Column(String(100), primary_key=True)
    firstname = Column(String(100))
    lastname = Column(String(100))
    nickname = Column(String(100))
    mail = Column(String(100))

    def __init__(self, uid='', firstname='', lastname='', nickname='', mail=''):
        if not isinstance( firstname, unicode ):
            firstname = unicode( firstname, 'utf-8' )
        if not isinstance( lastname, unicode ):
            lastname = unicode( lastname, 'utf-8' )
        if not isinstance( nickname, unicode ):
            nickname = unicode( nickname, 'utf-8' )
        if not isinstance( mail, unicode ):
            mail = unicode( mail, 'utf-8' )
        if not isinstance( uid, unicode ):
            uid  = unicode( uid, 'utf-8' )

        self.uid = uid
        self.firstname = firstname
        self.lastname = lastname
        self.nickname = nickname
        self.mail = mail

    def __repr__(self):
        return u"<Person('%s, %s')" % (self.uid, self.nickname)

def sync_users_with_ldap(config):
    ldap = LDAP(config)

    if not ldap.is_bind():
        return False

    lusers = ldap.fetch_all_users()
    if lusers:
        # clear user table...

        # add users from ldap
        for dn, ldap_dict in lusers:
            if ldap.verbose:
                log.debug("Find user: %r" % dn)

            uid       = ldap_dict.get( ldap.attr_uid )[0]
            firstname = ldap_dict.get( ldap.attr_givenname, [''])[0]
            lastname  = ldap_dict.get( ldap.attr_sn, [''])[0]
            nickname  = ldap_dict.get( ldap.attr_cn, [''])[0]
            mail      = ldap_dict.get( ldap.attr_mail, [''])[0]
            person = Person(uid=uid,
                            firstname=firstname,
                            lastname=lastname,
                            nickname=nickname,
                            mail=mail)

            Session.add(person)

        Session.commit()


 
# vim: et ts=4 sw=4
