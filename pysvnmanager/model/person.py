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

    lusers = {}
    for dn, ldap_dict in ldap.fetch_all_users():
        if ldap.verbose:
            log.debug("Find user: %r" % dn)
        uid = ldap_dict.get( ldap.attr_uid )[0]
        lusers[uid] = {
                        'dn':        dn,
                        'name':      uid,
                        'firstname': unicode(ldap_dict.get( ldap.attr_givenname, [''])[0], 'utf-8'),
                        'lastname':  unicode(ldap_dict.get( ldap.attr_sn, [''])[0], 'utf-8'),
                        'nickname':  unicode(ldap_dict.get( ldap.attr_cn, [''])[0], 'utf-8'),
                        'mail':      unicode(ldap_dict.get( ldap.attr_mail, [''])[0], 'utf-8') }

    dbusers = {}
    for person in Session.query(Person).all():
        dbusers[person.uid] = person

    lset  = set(lusers.keys())
    dbset = set(dbusers.keys())

    # add new record:
    db_commit = False
    for uid in lset - dbset:
        db_commit = True
        log.debug("add user: %r" % uid)

        person = Person(uid=uid,
                        firstname=lusers[uid]['firstname'],
                        lastname=lusers[uid]['lastname'],
                        nickname=lusers[uid]['nickname'],
                        mail=lusers[uid]['mail'])

        Session.add(person)

    if db_commit:
        Session.commit()

    # delete outofdate record
    db_commit = False
    for uid in dbset - lset:
        db_commit = True
        log.debug("Delete user: %r" % uid)

        Session.delete( dbusers[uid] )

    if db_commit:
        Session.commit()

    # update users
    db_commit = False
    for uid in dbset & lset:
        if ( dbusers[uid].firstname != lusers[uid]['firstname'] or
             dbusers[uid].lastname  != lusers[uid]['lastname'] or
             dbusers[uid].mail      != lusers[uid]['mail'] or
             dbusers[uid].nickname  != lusers[uid]['nickname'] ):
            db_commit = True
            log.debug("Update user: %r" % uid)

            Session.delete( dbusers[uid] )

            person = Person(uid=uid,
                            firstname=lusers[uid]['firstname'],
                            lastname=lusers[uid]['lastname'],
                            nickname=lusers[uid]['nickname'],
                            mail=lusers[uid]['mail'])

            Session.add(person)

    if db_commit:
        Session.commit()




# vim: et ts=4 sw=4
