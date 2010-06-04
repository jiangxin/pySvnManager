#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 OpenSourceXpress Ltd. (http://www.ossxp.com)
# Author: Jiang Xin
# Contact: http://www.ossxp.com
#          http://www.worldhello.net
#          http://moinmo.in/JiangXin
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

"""Subversion authz config file management.

Basic classes used for Subversion authz management.
"""

from configobj import ConfigObj
import rcsbackup as rcs
import re
import sys
import os
import my_fnmatch
import StringIO
import logging
log = logging.getLogger(__name__)

# i18n works only as pysvnmanager (a pylons app) model.
from pylons import config
if config.has_key('unittest'):
    from pylons.i18n import _
else:
    def _(message): return message

#reload(sys) # in Python2.5, method sys.setdefaultencoding 
            #will be delete after initialize. we need reload it.
#sys.setdefaultencoding('utf-8')

RIGHTS_W = 4
RIGHTS_R = 2
RIGHTS_NONE = 0
RIGHTS_RW = RIGHTS_R | RIGHTS_W
RIGHTS_ALL = RIGHTS_R | RIGHTS_W

def check_valid_username(name):
    bad_chars = r'''^[\.$&@~-]|[\\/:]|[*?"'<>|,;%#$]'''
    return check_valid_string(name, bad_chars=bad_chars)

def check_valid_aliasname(name):
    return check_valid_username(name)

def check_valid_groupname(name):
    if name == '*':
        return
    else:
        if name[0]=='$':
            name = name[1:]
        return check_valid_username(name)

def check_valid_reposname(name):
    if name == '/':
        return
    else:
        bad_chars = r'''^[\.$&@-]|[\\/:]|[*?"'<>|,;%#$]'''
        return check_valid_string(name, bad_chars=bad_chars)
    
def check_valid_string(check_str, bad_chars=""):
    check_str = normalize_user(check_str)
    msg = ''
    if not check_str:
        msg = _("Name is not given.")
    elif not isinstance(check_str, basestring):
        msg = _("Name is not string.")
    else:
        p = re.compile(bad_chars)
        if p.search(check_str):
            msg = _(u"Name (%s) contains invalid characters.") % check_str

    if msg:
        raise Exception, msg

def normalize_user(name):
    if isinstance(name, basestring):
        name = name.strip()

    if isinstance(name, str):
        name = unicode(name, 'utf-8')

    return name

def normalize_repos(name):
    if isinstance(name, basestring):
        name = name.strip()
        name = name.strip('/')
    if not name:
        name = '/'

    if isinstance(name, str):
        name = unicode(name, 'utf-8')

    return name

def normalize_path(name):
    if isinstance(name, basestring):
        name = name.strip()
        name = name.strip('/')
    if not name:
        name = '/'
    elif isinstance(name, basestring) and name[0] != '/':
        name = '/'+name
    
    if isinstance(name, str):
        name = unicode(name, 'utf-8')

    return name

class User(object):
    """User object used in groups, alias, and rules, etc.
    
    Useful attributes:
        name  : user login name.
        uname : unique name. compatible with Group, Alias objects.

    Method:
        attributes:

    >>> user = User('Jiang Xin')
    >>> user.name
    'Jiang Xin'
    >>> user.uname
    'Jiang Xin'
    >>> User('Jiang Xin') in user
    True
    >>> user in user
    True
    >>> 'Jiang Xin' in user
    True
    >>> 'jiang xin' in user
    True
    >>> user = User('')
    Traceback (most recent call last):
            ...
    Exception: Username is not provided
    """

    def __init__(self, name):
        name = normalize_user(name)

        if not name:
            raise Exception, 'Username is not provided'

        self.__name = name

    def __get_unique_name(self):
        return self.__name

    uname = property(__get_unique_name)
    name  = property(__get_unique_name)

    def __cmp__(self, obj):
        """For userlist sorting"""
        if isinstance(obj, User):
            return cmp(self.uname, obj.uname)
        else:
            return -1

    def __contains__(self, obj):
        """Match if is the same user.

        Compatible with Alias and Groups's __contains__ method."""
        if isinstance(obj, User):
            obj = obj.uname
        elif isinstance(obj, Alias):
            obj = obj.username
        elif isinstance(obj, (str, unicode)):
            obj = normalize_user(obj)
        else:
            return False

        if not obj:
            return False

        return obj.lower() == self.uname.lower()
    
    def __str__(self):
        return self.__name


class Alias(object):
    """Alias object used in groups, and rules.
    
    Alias is defined in svnauthz file like this:
        [aliases]
        aliasname = realuser
    
    Alias can be referenced in Group and rules as:
        [group]
        team1 = user1, &aliasname, @team2

        [repos:/trunk]
        * = 
        &aliasname = rw
    
    >>> user = User('username')
    >>> a = Alias('aliasname', user)
    >>> a.uname
    '&aliasname'
    >>> unicode(a)
    'aliasname = username'
    >>> user in a
    True
    >>> user = User('jiangxin')
    >>> a.user = user
    >>> unicode(a)
    'aliasname = jiangxin'
    >>> 'JiangXin' in a
    True
    >>> 'aliasname' in a
    False
    >>> '&aliasname' in a
    True
    >>> a in a
    True
    >>> a = Alias('admin')
    >>> unicode(a)
    'admin = '
    >>> a.username
    ''
    >>> '&admin' in a
    True
    >>> Alias('&aliasname')
    Traceback (most recent call last):
            ...
    Exception: Aliasname should not begin with &.
    >>> Alias('')
    Traceback (most recent call last):
            ...
    Exception: Aliasname is not provided.
    """

    def __init__(self, aliasname, userobj=None):
        if userobj != None and (not isinstance(userobj, User)) :
            raise Exception, 'Wrong parameter for userobj.'

        aliasname = normalize_user(aliasname)
        check_valid_aliasname(aliasname)
        self.__name = aliasname
        self.__userobj = userobj


    def __get_name(self):
        return self.__name

    name = property(__get_name)
    aliasname = property(__get_name)

    def __get_unique_name(self):
        return u'&'+self.__name

    uname = property(__get_unique_name)

    def __get_username(self):
        if self.__userobj:
            return self.__userobj.name
        else:
            return u''

    username = property(__get_username)

    def __set_user(self, userobj):
        if not isinstance(userobj, User):
            raise Exception, 'Wrong parameter for userobj.'
        self.__userobj = userobj

    user = property(__get_username, __set_user)

    def __str__(self):
        return u"%s = %s" % (self.aliasname, self.username)

    def __cmp__(self, obj):
        """For list sorting"""
        if isinstance(obj, Alias):
            return cmp(self.uname, obj.uname)
        else:
            return -1

    def __contains__(self, obj):
        if isinstance(obj, Alias):
            obj = obj.username
        elif isinstance(obj, (User, Group)):
            obj = obj.uname
        elif isinstance(obj, basestring):
            obj = normalize_user(obj)

        if not obj:
            return False

        obj = obj.lower()
        if obj == self.uname.lower() or \
              obj == self.username.lower():
            return True

        return False


class Group(object):
    """Group objects. Referenced in groups, and rules.
    
    Group is defined in svnauthz file like this:
        [group]
        team1 = user1, user2, &aliasname
    
    Group can be referenced in Group and rules as:
        [group]
        team1 = user1, user2, &aliasname, @team2
        team2 = user3, user4 

        [repos:/trunk]
        * = 
        @team1 = rw

    >>> authz = SvnAuthz()
    >>> user1 = authz.add_user('user1')
    >>> user2 = authz.add_user('user2')
    >>> user3 = authz.add_user('user3')
    >>> user4 = authz.add_user('user4')
    >>> jiangxin = authz.add_user('jiangxin')
    >>>
    >>> admin = authz.add_alias('admin', jiangxin)
    >>> N007  = authz.add_alias('N007', user4)
    >>>
    >>> admins = authz.add_group('admins')
    >>> team1  = authz.add_group('team1')
    >>> team2  = authz.add_group('team2')
    >>> team3  = authz.add_group('team3')
    >>> all    = authz.add_group('all')
    >>>
    >>> authz.add_group_member(admins, '&admin, &N007')
    ... # doctest: +ELLIPSIS
    <...object at ...>
    >>> authz.add_group_member(team1, [user1, team2]) 
    ... # doctest: +ELLIPSIS
    <...Group object at ...>
    >>> authz.add_group_member(team2, [user2, team3])
    ... # doctest: +ELLIPSIS
    <...Group object at ...>
    >>> authz.add_group_member(team3, [user3, team1], autodrop=True)
    ... # doctest: +ELLIPSIS
    <...Group object at ...>
    >>> authz.add_group_member(all, [team1, user3, user4])
    ... # doctest: +ELLIPSIS
    <...Group object at ...>
    >>>
    >>> print authz # doctest: +NORMALIZE_WHITESPACE
    # version : 0.0
    <BLANKLINE>
    [groups]
    admins = &N007, &admin
    all = @team1, user3, user4
    team1 = @team2, user1
    team2 = @team3, user2
    team3 = user3
    <BLANKLINE>
    [aliases]
    N007 = user4
    admin = jiangxin
    <BLANKLINE>
    <BLANKLINE>
    >>> jiangxin in admins
    True
    >>> 'user4' in admins
    True
    >>> 'user1' in admins
    False
    >>> '@team1' in team3
    False
    >>> 'user3' in team1
    True
    >>> star = authz.add_group('*')
    >>> anon = authz.add_group('$anonymous')
    >>> auth = authz.add_group('$authenticated')
    >>> print star
    # Built-in group: *
    >>> print anon
    # Built-in group: $anonymous
    >>> print auth
    # Built-in group: $authenticated
    >>> '*' in star
    True
    >>> 'valid_user' in star
    True
    >>> '$anonymous' in star
    True
    >>> '$authenticated' in star
    True
    >>> '*' in anon
    True
    >>> 'valid_user' in anon
    False
    >>> '$anonymous' in anon
    True
    >>> '$authenticated' in anon
    False
    >>> '*' in auth
    False
    >>> 'valid_user' in auth
    True
    >>> '$anonymous' in auth
    False
    >>> '$authenticated' in auth
    True
    """

    def __init__(self, name=''):
        name = normalize_user(name)
        check_valid_groupname(name)
        self.name = name
        self.__members = []

    def __get_unique_name(self):
        if self.name[0] != '$' and self.name != '*':
            return u'@'+self.name
        else:
            return self.name

    uname = property(__get_unique_name)

    def __get_member_names(self):
        if self.__members:
            return sorted(map(lambda x: x.uname, self.__members))
        else:
            return []

    membernames = property(__get_member_names)

    def __get_member_objs(self):
        return self.__members

    memberobjs = property(__get_member_objs)

    def __str__(self):
        if self.name[0] != '$' and self.name != '*':
            return u"%s = %s" % (self.name, ', '.join(sorted(self.membernames)))
        else:
            return u"# Built-in group: %s" % self.name

    def __iter__(self):
        for i in self.__members:
            yield i
    
    def __valid_group(self, groupobj, checked_groups=None):
        """x.valid_group(groupobj) -> bool

        Check if there is cycle reference in group defination."""
        if not checked_groups:
            checked_groups = [groupobj]
        for member in groupobj.memberobjs:
            if not isinstance(member, Group):
                continue
            if member in checked_groups:
                return False
            # Add group to hash of checked groups.
            checked_groups.append(member)
            # Check for deadly loop recursively.
            if not self.__valid_group(member, checked_groups):
                return False
            # Remove group to hash of checked groups. 
            # Other group members may contain this group
            checked_groups.remove(member)
        return True

    def append(self, *members, **opts):
        '''**opts: autodrop=False, raise Exception if recursive found.'''
        autodrop = opts.get('autodrop', False)
        for member in members:
            if isinstance(member, (list, tuple)):
                for i in member:
                    self.append(i, autodrop=autodrop)
                continue
            if not member in self.__members:
                self.__members.append(member)
                if not self.__valid_group(self):
                    self.__members.remove(member)
                    if not autodrop:
                        raise Exception, _('Recursive group membership for %s') \
                            % member.uname

    def remove(self, *members):
        ulist = []
        isRemoved = False
        for member in members:
            if isinstance(member, (str, unicode)):
                for user in member.split(','):
                    user = normalize_user(user)
                    if user:
                        ulist.append(user)
            elif isinstance(member, (list, tuple)):
                ulist.extend(member)
        
        mlist = map(lambda x: x.uname, self.__members)
        for user in ulist:
            if isinstance(user, (str, unicode)):
                user = normalize_user(user)
                if user not in mlist:
                    continue
                del self.__members[mlist.index(user)]
                isRemoved = True
            else:
                if user in self.__members:
                    self.__members.remove(user)
                    isRemoved = True
            mlist = map(lambda x: x.uname, self.__members)
        
        return isRemoved

    def remove_all(self):
        self.__members = []

    def __cmp__(self, obj):
        """For list sorting"""
        if isinstance(obj, Group):
            return cmp(self.uname, obj.uname)
        else:
            return -1

    def __contains__(self, obj):

        if isinstance(obj, Alias):
            obj = obj.username
        elif isinstance(obj, (User, Group)):
            obj = obj.uname
        elif isinstance(obj, (str, unicode)):
            obj = normalize_user(obj)
        else:
            return False

        if not obj:
            return False

        obj = obj.lower()
        if obj == self.uname.lower():
            return True

        if self.uname == '*':
            return True
        if self.uname == '$anonymous' and obj == '*':
            return True
        if self.uname == '$authenticated':
            if obj != '$anonymous' and obj != '*':
                return True

        for member in self.__members:
            if obj in member:
                return True

        return False


class UserList(object):
    """Store all users referenced by [group], [aliases], [repos:/a/b] sections.
    """
    def __init__(self):
        self._user_list = []

    def __get_user_list(self):
        self._user_list.sort()
        return self._user_list

    user_list = property(__get_user_list)

    def __iter__(self):
        for i in self.user_list:
            yield i

    def get(self, name):
        return self.get_or_set(name, autocreate=False)

    def get_or_set(self, name, autocreate = True):
        assert isinstance(name, basestring)
        
        name = normalize_user(name)
        if not name:
            return None
        if name[0] == '&' or name[0] == '@' or name[0] == '$' or name=='*':
            raise Exception, _("Not a valid username: %s") % name

        for user in self._user_list:
            if user.name == name:
                return user

        if autocreate:
            check_valid_username(name)
            user = User(name)
            self._user_list.append(user)
            return user
        else:
            return None


class AliasList(object):
    """Store all alias objects defined by [aliases] section or referenced in 
    [group], [repos:/path/to] but not be set.
    """
    def __init__(self):
        self._alias_list = []

    def __get_alias_list(self):
        self._alias_list.sort()
        return self._alias_list

    alias_list = property(__get_alias_list)

    def __iter__(self):
        for i in self.alias_list:
            yield i

    def get(self, name):
        return self.get_or_set(name, False)

    def get_or_set(self, name, autocreate = True):
        assert isinstance(name, basestring)
        name = normalize_user(name)

        if not name:
            return None
        if name[0] == '&':
            name = name[1:]
        for alias in self._alias_list:
            if alias.aliasname == name:
                return alias

        if autocreate:
            check_valid_aliasname(name)
            alias = Alias(name)
            self._alias_list.append(alias)
            return alias
        else:
            return None

    def remove(self, name):
        if isinstance(name, (str, unicode)):
            alias = self.get(name)
        else:
            alias = name
        if alias and alias in self._alias_list:
            self._alias_list.remove(alias)
            return True
        else:
            return False

    def __str__(self):
        buff = u"[aliases]\n"
        for alias in self.alias_list:
            buff += unicode(alias)
            buff += u'\n'
        return buff


class GroupList(object):
    """Store all group objects defined by [groups] section or referenced in 
    [groups], [repos:/path/to] but not be set.
    """
    def __init__(self):
        self._group_list = []

    def __iter__(self):
        for i in self.group_list:
            yield i

    def __get_group_list(self):
        self._group_list.sort()
        return self._group_list

    group_list = property(__get_group_list)

    def get(self, name):
        return self.get_or_set(name, False)

    def get_or_set(self, name, autocreate = True):
        assert isinstance(name, basestring)
        name = normalize_user(name)
        if not name:
            return None
        if name[0] == '@':
            name = name[1:]
        for group in self._group_list:
            if group.name == name:
                return group

        if autocreate:
            check_valid_groupname(name)
            group = Group(name)
            self._group_list.append(group)
            return group
        else:
            return None

    def remove(self, name, force=False):
        if isinstance(name, Group):
            name = name.name
        else:
            name = normalize_user(name)
        item = self.get(name)
        if item:
            for group in self._group_list:
                if group == item:
                    continue
                if item in group.memberobjs:
                    if force:
                        group.memberobjs.remove(item)
                        assert not item in group.memberobjs
                    else:
                        raise Exception, \
                                _('Group %s is referenced by group %s.') \
                                % (name, group.uname)
            self._group_list.remove(item)
            return True
        else:
            return False

    def __str__(self):
        buff = u"[groups]\n"
        for group in self.group_list:
            if group.name[0] != '$' and group.name != '*':
                buff += unicode(group)
                buff += u'\n'
        return buff


class Rule(object):
    """Store one single svnauthz rule.

    Attribute:
        userobj -- points to a user/group/alias object. Has a match method, 
                              which can detect whether the rule hits certain 
                              user/group/alias object.
        uname   -- the same as userobj's uname attribute.
        rights  -- for convenience allow two different ways to save rights:
                                  Set the rights using str: as 'r', 'rw', ''. or 
                                  Set with raw bits value: RIGHTS_R, RIGHTS_W, ...
                              Rights property return only raw bits, remember.
    """
    def __init__(self, userobj):
        self.userobj = userobj
        self.__rights = RIGHTS_NONE

    def __get_unique_name(self):
        return self.userobj.uname

    uname = property(__get_unique_name)

    def __set_rights(self, rights):
        if isinstance(rights, (str, unicode)):
            rights = rights.strip().lower()
            rbit = RIGHTS_NONE
            if 'r' in rights:
                rbit |= RIGHTS_R
            if 'w' in rights:
                rbit |= RIGHTS_W
            rights = rbit
        else:
            rights = int(rights) & RIGHTS_ALL

        self.__rights = rights

    def __get_rights(self):
        return self.__rights

    rights = property(__get_rights, __set_rights)

    def get_permission(self, userobj):
        """x.get_permission(userobj) -> (permit_bits, deny_bits)

        If userobj match with rule's userobj, return permit and deny bits.
        Else return (ZERO, ZERO)
        """
        if not userobj in self.userobj:
            return (RIGHTS_NONE, RIGHTS_NONE)

        perm = self.rights
        deny = RIGHTS_ALL ^ perm
        return (perm, deny)

    def __str__(self):
        rstr = u''
        rbit = self.__rights
        if rbit & RIGHTS_R:
            rstr += u'r'
        if rbit & RIGHTS_W:
            rstr += u'w'
        return u"%s = %s" % (self.userobj.uname, rstr)

    def __cmp__(self, obj):
        """For list sorting"""
        if isinstance(obj, Rule):
            return cmp(self.userobj.uname, obj.userobj.uname)
        else:
            return -1


class Module(object):
    """Module stores one svnauthz module config section as [repos:/path/to].

    A module has a repos name store in repos, and path of the module.
    Also the main part is rule_list[], store a list of Rule objects
    for this module.
    """
    def __init__(self, repos, path):
        self.repos = normalize_repos(repos)
        self.path  = normalize_path(path)
        self.__rule_list  = []

    def __iter__(self):
        for i in self.__rule_list:
            yield i
    
    def __get_fullame(self):
        return self.repos+':'+self.path

    fullname = property(__get_fullame)

    def clean_rules(self):
        self.__rule_list = []

    def del_rule(self, rules):
        if isinstance(rules, (str, unicode)):
            rdict = {}
            key, value = rules.split('=', 1)
            rdict[key.strip()] = value.strip()
            return self.del_rule(rdict)
        elif isinstance(rules, (list, tuple)):
            for rule in rules:
                self.del_rule(rule)
            return True

        if not isinstance(rules, dict):
            raise

        unamelist = map(lambda x: x.uname, self.__rule_list)
        for (user, rights) in rules.items():
            user = normalize_user(user)

            if user in unamelist:
                del self.__rule_list[unamelist.index(user)]
                unamelist = map(lambda x: x.uname, self.__rule_list)

        return True

    def update_rule(self, obj, rights):
        unamelist = map(lambda x: x.uname, self.__rule_list)
        if obj.uname in unamelist:
            rule = self.__rule_list[unamelist.index(obj.uname)]
        else:
            rule = Rule(obj)
            self.__rule_list.append(rule)
        rule.rights = rights

        return True

    def __get_rules(self):
        return self.__rule_list
   
    rules = property(__get_rules)
    
    def __str__(self):
        if not self.__rule_list:
            return u''
        if self.repos == '/' or not self.repos:
            buff = u"[%s]\n" % self.path
        else:
            buff = u"[%s:%s]\n" % (self.repos, self.path)
        for rule in sorted(self.__rule_list):
            tmp = unicode(rule)
            if tmp:
                buff += tmp
                buff += u'\n'
        return buff

    def __cmp__(self, obj):
        """For list sorting"""
        if isinstance(obj, Module):
            return cmp(self.fullname, obj.fullname)
        else:
            return -1

    def get_permit_bits(self, user):
        """x.get_permit_bits(user) -> (perm, deny)
        
        Return permission bits of this module as a tuple.

        Warning: the return value is meaningful only if access_is_determined 
        returns True. Check return value of access_is_determined first!
        """
        perm = RIGHTS_NONE
        deny = RIGHTS_NONE
        for rule in self.__rule_list:
            pbits, dbits = rule.get_permission(user)
            perm |= pbits
            deny |= dbits
        return (perm, deny)

    def get_permit_str(self, user):
        """x.get_permit_str(user) -> string
        
        Return user friendly permission of this module.

        Warning: the return value is meaningful only if access_is_determined 
        returns True. Check return value of access_is_determined first!
        """
        permstr = ''
        perm, deny = self.get_permit_bits(user)
        if perm & RIGHTS_R:
            permstr += 'r'
        if perm & RIGHTS_W:
            permstr += 'w'
        return permstr

    def access_is_determined(self, user):
        """x.access_is_determined(user) -> bool
        
        Whether a certain user object matches with some of 
        the rules for this module.

        Permission return by other funtions is meaningful only if the method
        returns True.
        """
        perm, deny = self.get_permit_bits(user)
        if (RIGHTS_ALL & perm) or (RIGHTS_ALL & deny):
            return True
        else:
            return False

    def access_is_granted(self, user, required):
        """x.access_is_granted(user, required) -> bool
        
        Whether the user required rights is granted by rules of this module.

        Warning: the return value is meaningful only if access_is_determined 
        returns True. Check return value of access_is_determined first!
        """
        if isinstance(required, (str, unicode)):
            required = required.strip().lower()
            rbit = RIGHTS_NONE
            if 'r' in required:
                rbit |= RIGHTS_R
            if 'w' in required:
                rbit |= RIGHTS_W
            required = rbit
        else:
            required = int(required) & RIGHTS_ALL
        perm, deny = self.get_permit_bits(user)
        if deny & required == RIGHTS_NONE:
            return True
        elif perm & required == required & RIGHTS_ALL:
            return True
        else:
            return False


class Repos(object):
    """One repos may contain many modules.

    These modules share the same repos name, and have the same administrator(s).
    """
    def __init__(self, name):
        name = normalize_repos(name)
        self.__repos_name = name
        self.__admins = []
        self.module_list = []

    def __iter__(self):
        for i in self.module_list:
            yield i
    
    def __get_name(self):
        return self.__repos_name

    def __set_name(self, name):
        self.__repos_name = normalize_repos(name)

    name = property(__get_name, __set_name)

    def __get_path_list(self):
        return map(lambda x:x.path, self.module_list)
    
    path_list = property(__get_path_list)

    def __get_admins(self):
        alist = [i.uname for i in self.__admins]
        return ', '.join(sorted(alist))

    def __set_admins(self, admins):
        self.__admins = []
        return self.add_admin(admins)

    admins = property(__get_admins, __set_admins)
    
    def add_admin(self, admin):
        """x.add_admin(admin)"""
        if isinstance(admin, (User, Group, Alias)):
            if not admin in self.__admins:
                self.__admins.append(admin)
        elif isinstance(admin, (list, tuple, set)):
            for i in admin:
                self.add_admin(i)
        else:
            raise Exception, "unknown user: %s, type: %s" % (admin, type(admin))

    def del_admin(self, admin):
        if isinstance(admin, (list, tuple, set)):
            for i in admin:
                self.del_admin(i)
        elif isinstance(admin, (User, Group, Alias)):
            self.__admins.remove(admin)
        else:
            raise Exception, "unknown user: %s, type: %s" % (admin, type(admin))
    
    def add_module(self, path):
        path = normalize_path(path)

        for i in self.module_list:
            if i.path.lower() == path.lower():
                return i
        i = Module(repos=self.name , path=path)
        self.module_list.append(i)
        return i

    def del_module(self, path):
        path = normalize_path(path)

        mlist = map(lambda x: x.path, self.module_list)
        if path in mlist:
            del self.module_list[mlist.index(path)]
            return True
        else:
            return False

    def del_all_modules(self):
        self.module_list = []

    def get_module(self, path):
        path = normalize_path(path)

        for i in self.module_list:
            if i.path.lower() == path.lower():
                return i
        # OSSXP hacked subversion supports wildcard characters as module path.
        for i in self.module_list:
            if '*' in i.path or '?' in i.path:
                if my_fnmatch.fnmatch(path, i.path):
                    return i
        return None

    def is_blank(self):
        if self.__admins or self.module_list:
            return False
        else:
            return True

    def __str__(self):
        buff = u''
        for i in sorted(self.module_list):
            tmp = unicode(i)
            if tmp:
                buff += tmp
                buff += u'\n'
        return buff

    def __cmp__(self, obj):
        """For list sorting"""
        if isinstance(obj, Repos):
            return cmp(self.name, obj.name)
        else:
            return -1


class ReposList(object):
    def __init__(self):
        self.repos_list = []
        self.get_or_set('/')

    def __iter__(self):
        for i in self.repos_list:
            yield i

    def get(self, name):
        return self.get_or_set(name, False)

    def get_or_set(self, name, autocreate = True):
        name = normalize_repos(name)
        assert isinstance(name, basestring)

        for repos in self.repos_list:
            if repos.name.lower() == name.lower():
                return repos

        if autocreate:
            check_valid_reposname(name)
            repos = Repos(name)
            self.repos_list.append(repos)
            return repos
        else:
            return None

    def remove(self, name, recursive=False):
        if isinstance(name, Repos):
            name = name.name

        name = normalize_repos(name)

        if name == '/' and not recursive:
            return False

        rlist = map(lambda x: x.name, self.repos_list)
        try:
            idx = rlist.index(name)
        except:
            raise Exception, "Repos '%s' not exist" % name

        repos = self.repos_list[idx]
        assert(repos.name.lower() == name.lower())

        if recursive:
            if name == '/':
                self.repos_list[idx].del_all_modules()
            else:
                del self.repos_list[idx]
            return True

        else:
            if repos.is_blank():
                del self.repos_list[idx]
                return True
            else:
                return False

    def __str__(self):
        buff = u''
        for repos in sorted(self.repos_list):
            tmp = unicode(repos)
            if tmp:
                buff += tmp
                ##buff += '\n'
        return buff


class SvnAuthz(object):
    '''
    Data structure:
    * SvnAuthz
            * UserList  user_list
                    * User  user_list[]
            * AliasList alias_list
                    * Alias alias_list[]
            * GroupList group_list
                    * Group group_list[]
            * ReposList repos_list
                    * Repos repos_list[]
                            str __repos_name
                            __admins = set(str[])
                            * Module module_list[]
                                    str repos
                                    str path
                                    * Rule rule_list[]
                                          Group/Alias/User id
                                          str right
    '''
    def __init__(self, fileobj=None):
        self.__clear()
        self.__file = None
        # Used as check-in username to rcs file.
        self.login_as = None
        # Used as check-in message to rcs file.
        self.comment = []
        self.load(fileobj)
    
    def __clear(self):
        self.__userlist  = UserList()
        self.__aliaslist = AliasList()
        self.__grouplist = GroupList()
        self.__reposlist = ReposList()
        self.__version = '0.0'
        self.config = None
        self.add_repos('/')        

    def __get_userlist(self):
        return self.__userlist

    userlist = property(__get_userlist)

    def __get_aliaslist(self):
        return self.__aliaslist

    aliaslist = property(__get_aliaslist)

    def __get_grouplist(self):
        return self.__grouplist

    grouplist = property(__get_grouplist)

    def __get_reposlist(self):
        return self.__reposlist

    reposlist = property(__get_reposlist)

    def __get_version(self):
        return self.__version
    
    version = property(__get_version)
    
    def update_revision(self):
        major, minor = self.version.rsplit('.',1)
        if minor.isdigit():
            rev = int(minor)+1
        else:
            rev = 0
        self.__version = u"%s.%d" % (major, rev)
        
    def modulelist(self):
        for i in self.reposlist:
            for j in i.module_list:
                yield j

    def rulelist(self):
        for i in self.reposlist:
            for j in i.module_list:
                for k in j:
                    yield k

    def load(self, fileobj=None):
        '''
        Initial SvnAuthz from authz file.
        file can be filename, or file handler, StingIO,...
        '''
        self.__clear()
        
        self.__file = fileobj
        if self.__file:
            assert isinstance(self.__file, (basestring, file, StringIO.StringIO))
            # set encoding to 'utf8'
            self.config = ConfigObj(self.__file, encoding='utf8', default_encoding='utf8')

            if self.config:
                self.parse_acl()
                self.parse_version()
                if self.config.has_key('groups'):
                    self.parse_groups(self.config['groups'])
                if self.config.has_key('aliases'):
                    self.parse_aliases(self.config['aliases'])
                for (section, contents) in self.config.items():
                    if section == 'groups' or section == 'aliases':
                        continue
                    self.parse_module(section, contents)

    def save(self, revision, comment=""):
        if comment: self.comment.append(comment)
            
        if self.__file:
            assert isinstance(self.__file, (basestring, StringIO.StringIO))
            #if not revision:
            #    revision = self.version
            last_rev = self.get_revision_from_file()
            log.debug("this revision: %s, last: %s" % (revision, last_rev))
            if last_rev and revision != last_rev:
                raise Exception, _("Update failed! You are working on a out-of-date revision.") + " (%s <> %s)" % (revision, last_rev)

            self.update_revision()

            if isinstance(self.__file, basestring):
                f = open(self.__file, 'w')
            else:
                f = self.__file
                f.truncate(0)
            f.write(unicode(self).encode('utf-8'))
            if isinstance(self.__file, (basestring)):
                f.close()
            else:
                f.seek(0,0)
                f.flush()

            if isinstance(self.__file, basestring):
                try:
                    self.validate_authz_file(self.__file)
                except Exception, e:
                    rcs.restore(self.__file)
                    raise Exception, e
                else:
                    rcs.backup(self.__file, comment=self.comment, user=self.login_as)

        self.comment = []
    
    def validate_authz_file(self, filename):
        if isinstance(filename, basestring):
            stat = os.stat(filename)
            if stat.st_size == 0:
                raise Exception, "Size of file (%s) is zero!" % filename
            
            try:
                from svn import repos as _repos
                _repos.authz_read(filename, 1)
            except ImportError:
                pass
    
    def __str__(self):
        buff = u""
        buff += self.compose_version()
        buff += self.compose_acl()
        buff += u'\n'
        buff += unicode(self.__grouplist)
        buff += u'\n'
        buff += unicode(self.__aliaslist)
        buff += u'\n'
        buff += unicode(self.__reposlist)
        return buff

    def differ(self):
        if isinstance(self.__file, basestring):
            contents_old = unicode(open(self.__file, 'r').read().strip(), "utf-8", "ignore")
        elif isinstance(self.__file, (file, StringIO.StringIO)):
            self.__file.seek(0)
            contents_old = unicode(self.__file.read().strip(), "utf-8", "ignore")
            self.__file.seek(0)
        else:
            return u''
        contents_new = unicode(self).strip()
        if  contents_new != contents_old:
            import difflib
            difflines = []
            for line in difflib.unified_diff(contents_old.splitlines(), contents_new.splitlines(), 'old authz', 'new authz', lineterm=''):
                difflines.append(line)
                if len(difflines)>10:
                    break
            return u'\n'.join(difflines)
        return u''
 
    def parse_groups(self, groups):
        for (name, members) in groups.items():
            group = self.__grouplist.get_or_set(name)
            self.add_group_member(group, members, autodrop=True)

    def parse_module(self, section, contents):
        section = section.strip()

        if ':' in section:
            reposname, path = section.split(':', 1)
        else:
            reposname = '/'
            path = section

        reposname = normalize_repos(reposname)
        path = normalize_path(path)

        self.add_rules(reposname, path, contents, force=True)

    def parse_aliases(self, aliases):
        for (name, username) in aliases.items():
            name = normalize_user(name)
            username = normalize_user(username)
            self.add_alias(name, username)

    def parse_acl(self):
        acls = self.config.initial_comment
        pattern = re.compile(r'^#\s*admin\s*:\s*(.+?)\s*=\s*(.+?)\s*(?:#.*)?$')
        if acls:
            for acl in acls:
                i = pattern.search(acl)
                if i:
                    name  = normalize_repos(i.group(1))
                    admin = normalize_user(i.group(2))
                    if name and admin:
                        repos = self.__reposlist.get_or_set(name)
                        self.set_admin(admin, repos)

    def parse_version(self):
        ic = self.config.initial_comment
        pattern = re.compile(r'^#\s*version\s*[:=]\s*(.+?)\s*(?:#.*)?$')
        if ic:
            for line in ic:
                i = pattern.search(line)
                if i:
                    version  = i.group(1)
                    if version:
                        self.__version = version
                        break

    def get_revision_from_file(self):
        if not self.__file:
            return ''
        else:
            assert isinstance(self.__file, (basestring, file, StringIO.StringIO))
            if isinstance(self.__file, basestring):
                f = open(self.__file)
            else:
                f = self.__file
                f.seek(0,0)
            pattern = re.compile(r'^#\s*version\s*[:=]\s*(.+?)\s*(?:#.*)?$')
            version = ""
            for line in f:
                i = pattern.search(line)
                if i:
                    version  = i.group(1)
                    break
            if isinstance(self.__file, (basestring)):
                f.close()
            else:
                f.seek(0,0)
            return version

    def compose_version(self):
        buff = ""
        if self.__version:
            buff = u"# version : %s\n" % self.__version
        return buff

    def compose_acl(self):
        buff = u""
        for repos in self.__reposlist:
            admins = repos.admins
            if admins:
                buff += u"# admin : %s = %s\n" % (repos.name, admins)
        return buff

    def is_admin(self, user, repos='/', admins=None):
        if isinstance(user, User):
            user = user.uname
        elif isinstance(user, Alias):
            user = user.username
        elif isinstance(user, basestring):
            user = normalize_user(user)
        elif not user:
            return False

        if isinstance(repos, basestring):
            repos = self.__reposlist.get(repos)
        
        if repos:
            if admins is None:
                admins = repos.admins
            for i in admins.split(','):
                if i: i = normalize_user(i)
                
                if not i: continue
                
                if user == i:
                    return True

                i = self.get_userobj(i, autocreate=False)

                if i and user in i:
                    return True

        if not repos or repos.name != '/':
            return self.is_admin(user, '/')
        else:
            return False

    def is_super_user(self, user):
        return self.is_admin(user, '/')
    
    def set_admin(self, admins, repos=None):
        if not isinstance(repos, Repos):
            repos = self.__reposlist.get(repos)
        if not repos:
            return False
        
        if isinstance(admins, basestring):
            alist = [x.strip() for x in admins.split(',')]
        elif isinstance(admins, (list, tuple, set)):
            alist = admins
        else:
            alist = [admins]
        ulist = []
        for i in alist:
            if isinstance(i, (User, Group, Alias)):
                ulist.append(i)
            elif not i:
                continue
            elif isinstance(i, basestring):
                ulist.append(self.get_userobj(i, autocreate=True))
            else:
                raise Exception, "unknown user: %s, type: %s" % (i, type(i))

        repos.admins = ulist

        return True

    def add_repos(self, reposname):
        repos = self.__reposlist.get_or_set(reposname)
        return repos

    def get_repos(self, reposname):
        repos = self.__reposlist.get(reposname)
        return repos

    def del_repos(self, name, recursive=False):
        return self.__reposlist.remove(name, recursive)

    def add_module(self, reposname, path):
        repos = self.__reposlist.get_or_set(reposname)
        module = repos.add_module(path)
        return module

    def get_module(self, reposname, path):
        repos = self.__reposlist.get(reposname)
        if repos:
            module = repos.get_module(path)
            return module
        else:
            return None

    def del_module(self, reposname, path):
        repos = self.__reposlist.get(reposname)
        if repos:
            return repos.del_module(path)
        return False

    def add_rules(self, reposname, path, rules, force=False):
        module = self.get_module(reposname, path)
        if not module:
            if force:
                module = self.add_module(reposname, path)
            else:
                raise Exception, 'No module exist for %s:%s' % (reposname, path)

        rdict = {}
        if isinstance(rules, (str, unicode)):
            rules = rules.strip()
            if '\n' in rules:
                rule_list = rules.split('\n')
            elif ';' in rules:
                rule_list = rules.split(';')
            else:
                rule_list = [rules,]
            for rule in rule_list:
                rule = rule.strip()
                if not rule:
                    continue
                if '=' in rule:
                    key, value = rule.split('=', 1)
                    rdict[key.strip()] = value.strip()
                else:
                    raise Exception, _('Unknown rule format: %s') % rule
        elif isinstance(rules, (list, tuple)):
            for rule in rules:
                if '=' in rule:
                    key, value = rule.split('=', 1)
                    rdict[key.strip()] = value.strip()
                else:
                    raise Exception, _('Unknown rule format: %s') % rule
        elif isinstance(rules, dict):
            rdict = rules
        else:
            raise Exception, _('Unknown rule format: %s') % rules

        for (name, rights) in rdict.items():
            obj = self.get_userobj(name, autocreate=True)
            module.update_rule(obj, rights)

        return True

    def set_rules(self,reposname, path, rules, reset=True, force=False):
        module = self.get_module(reposname, path)
        if not module:
            #if force:
            #    module = self.add_module(reposname, path)
            #else:
            raise Exception, _('No module exist for %s:%s') % (reposname, path)

        if reset:
            module.clean_rules()

        return self.add_rules(reposname, path, rules, force=force)
 
    def get_userobj(self, name, autocreate=False):
        name = normalize_user(name)

        if not name:
            return None
        if name[0] == '@' or name[0] == '$' or name == '*':
            obj = self.grouplist.get_or_set(name, autocreate = autocreate)
        elif name[0] == '&':
            obj = self.aliaslist.get_or_set(name, autocreate = autocreate)
        else:
            obj = self.userlist.get_or_set(name, autocreate = autocreate)
        return obj

    def get_manageable_repos_list(self, username):
        repos_list = []
        if self.is_admin(username, '/'):
            repos_list.extend(map(lambda x:x.name, self.reposlist))
        else:
            for i in self.reposlist:
                if self.is_admin(username, i):
                    repos_list.append(i.name)
        return sorted(repos_list)
        
    def del_rule(self, reposname, path, rule):
        module = self.get_module(reposname, path)
        if not module:
            return False
        return module.del_rule(rule)

    def add_group(self, name, members=None, autodrop=False):
        group = self.__grouplist.get_or_set(name)
        if members:
            return self.add_group_member(group, members, autodrop=autodrop)
        return group

    def set_group(self, name, members, autodrop=False):
        group = self.__grouplist.get_or_set(name)
        group.remove_all()
        if members:
            return self.add_group_member(group, members, autodrop=autodrop)
        return group

    def del_group(self, name, force=False):
        self.chk_grp_ref_by_rules(name)
        return self.__grouplist.remove(name, force=force)

    def add_group_member(self, group, members, autodrop=False):
        if isinstance(group, basestring):
            groupobj = self.__grouplist.get_or_set(group)
        else:
            groupobj = group

        ulist = []
        if isinstance(members, (str, unicode)):
            for user in members.split(','):
                user = normalize_user(user)
                if user:
                    ulist.append(user)
        elif isinstance(members, (list, tuple)):
            ulist.extend(members)
        else:
            ulist.append(members)

        for user in ulist:
            if isinstance(user, (User, Group, Alias)):
                member = user
            else:
                member = self.get_userobj(user, autocreate=True)
            if member:
                groupobj.append(member, autodrop=autodrop)

        return groupobj

    def del_group_member(self, groupname, username):
        group = self.__grouplist.get_or_set(groupname)
        return group.remove(username)

    def add_user(self, username):
        username = normalize_user(username)
        userobj = self.userlist.get_or_set(username)
        return userobj

    def add_alias(self, aliasname, user=None):
        alias = self.__aliaslist.get_or_set(aliasname)
        if isinstance(user, basestring):
            user = self.userlist.get_or_set(user)
        if user:
            alias.user = user
        return alias

    def del_alias(self, name, force=False):
        alias = self.__aliaslist.get(name)
        if not alias:
            return False

        self.chk_alias_ref_by_rules(alias)

        for group in self.__grouplist:
            if alias in group.memberobjs:
                if force:
                    group.memberobjs.remove(alias)
                else:
                    raise Exception, \
                        _('Alias %s is referenced by group %s.') % \
                            (alias.uname, group.uname)
        return self.__aliaslist.remove(name)

    def __check_ref_by_rules(self, name):
        if name:
            if isinstance(name, (User, Group, Alias)):
                name = name.uname

            for i in self.modulelist():
                ulist = map(lambda x:x.uname, i)
                if name in ulist:
                    raise Exception, _("%s is referenced by [%s].") % \
                            (name, i.fullname)

    def chk_alias_ref_by_rules(self, name):
        if isinstance(name, (str, unicode)):
            if name and name[0] != '&':
                name = '&'+name
        return self.__check_ref_by_rules(name)

    def chk_grp_ref_by_rules(self, name):
        if isinstance(name, (str, unicode)):
            if name and name[0] != '@' and name[0] != '$' and name != '*' :
                name = '@'+name
        return self.__check_ref_by_rules(name)

    def check_rights(self, user, repos, path, required):
        if isinstance(user, (str, unicode)):
            user = normalize_user(user)
        if isinstance(repos, (str, unicode)):
            repos = normalize_repos(repos)
        if isinstance(path, (str, unicode)):
            path  = normalize_path(path)

        if isinstance(required, (str, unicode)):
            required = required.strip()
        else:
            required = int(required) & RIGHTS_ALL

        if not user:
            user = '*'
        if not repos:
            repos = '/'
        if not path:
            path  = '/'

        module = self.get_module(repos, path)
        if module:
            if module.access_is_determined(user):
                return module.access_is_granted(user, required)

        if repos != '/':
            module = self.get_module('/', path)
            if module:
                if module.access_is_determined(user):
                    return module.access_is_granted(user, required)

        if '/' in path and path != '/':
            path = path.rsplit('/', 1)[0]
            return self.check_rights(user, repos, path, required)
        else:
            return False

    def get_rights(self, user, repos, path):
        user = normalize_user(user)
        repos = normalize_repos(repos)
        path = normalize_path(path)

        module = self.get_module(repos, path)
        if module:
            if module.access_is_determined(user):
                return module.get_permit_bits(user)

        if repos != '/':
            module = self.get_module('/', path)
            if module:
                if module.access_is_determined(user):
                    return module.get_permit_bits(user)

        if '/' in path and path != '/':
            path = path.rsplit('/', 1)[0]
            return self.get_rights(user, repos, path)
        else:
            return (RIGHTS_NONE, RIGHTS_ALL)

    def get_access_map(self, user=None, reposname='/', descend=True):
        if isinstance(user, (str, unicode)):
            user = normalize_user(user)
        if not user:
            user = '*'
        reposname = normalize_repos(reposname)
        repos = self.get_repos(reposname)
        if not repos:
            if descend and reposname != '/':
                return self.get_access_map(user, '/')
            return None

        path_set = set(map(lambda x:x.path, repos.module_list))
        read_path_set = set()
        write_path_set = set()
        deny_path_set = set()

        if reposname != '/':
            root_path_set = set(map(lambda x:x.path, 
                                    self.get_repos('/').module_list))
            path_set = path_set.union(root_path_set)

        for path in path_set:
            perm, deny = self.get_rights(user, reposname, path)
            if perm & RIGHTS_W:
                write_path_set.add(path)
            elif perm & RIGHTS_R:
                read_path_set.add(path)
            else:
                deny_path_set.add(path)
        return { 
                'write':write_path_set, 
                'read': read_path_set, 
                'deny': deny_path_set }

    def get_path_access_msgs(self, user, reposname, path, abbr=False):
        if isinstance(user, (str, unicode)):
            user = normalize_user(user)
        if not user:
            user = '*'
        if reposname:
            reposname = normalize_repos(reposname)
        if path:
            path = normalize_path(path)
        msgs = []
        if not reposname or reposname=='*' or reposname=='...':
            reposname = sorted(map(lambda x: x.name, self.__reposlist))
        
        if isinstance(reposname, (list, tuple)):
            for i in reposname:
                msgs.extend(self.get_path_access_msgs(user, i, path, abbr))
        else:
            perm, deny = self.get_rights(user, reposname, path)
            if abbr:
                tmpstr = '[%s:%s] %s =' % ( reposname, path, user)
                if perm & RIGHTS_W:
                    tmpstr += ' rw'
                elif perm & RIGHTS_R:
                    tmpstr += ' r'
                msgs.append(tmpstr)
            else:
                if perm & RIGHTS_W:
                    msgs.append(_('User %(username)s has Full (RW) rights for module %(repos)s:%(path)s') % {'username':user, 'repos':reposname, 'path':path})
                elif perm & RIGHTS_R:
                    msgs.append(_('User %(username)s has ReadOnly (RO) rights for module %(repos)s:%(path)s') % {'username':user, 'repos':reposname, 'path':path})
                else:
                    msgs.append(_('User %(username)s can *NOT* access to module %(repos)s:%(path)s') % {'username':user, 'repos':reposname, 'path':path})
            
        return msgs

    def get_access_map_msgs(self, user='*', reposname=None, abbr=False):
        if isinstance(user, (str, unicode)):
            user = normalize_user(user)
        if not user:
            user = '*'

        if isinstance(reposname, basestring):
            reposname = normalize_repos(reposname)

        maps = []
        msgs = []
        if not reposname or reposname=='*' or reposname=='...':
            reposname = [r.name for r in sorted(self.__reposlist)]
        
        if isinstance(reposname, (list, tuple)):
            for i in reposname:
                #map = self.get_access_map(user, i, descend=False)
                map = self.get_access_map(user, i)
                log.debug("repos:%s, map: %s" % (i, map))
                if map:
                    map['user'] = unicode(user)
                    map['repos'] = i
                    maps.append(map)
        else:
            map = self.get_access_map(user, reposname)
            if map: 
                map['user'] = unicode(user)
                map['repos'] = reposname
                maps.append(map)

        for map in maps:
            if abbr:
                write_list = ', '.join(sorted(map['write']))
                read_list  = ', '.join(sorted(map['read']))
                deny_list  = ', '.join(sorted(map['deny']))

                msg = _('''
%(user)s => [%(repos)s]
%(sep)s
RW: %(write)s
RO: %(read)s
XX: %(deny)s
\n''') %  { 
                 'repos' : map['repos'], 
                 'user'  : map['user'], 
                 'sep'   : '-'*40, 
                 'write' : write_list, 
                 'read'  : read_list, 
                 'deny'  : deny_list, 
                }
            else:
                write_list = '    '+'\n    '.join(sorted(map['write']))
                read_list  = '    '+'\n    '.join(sorted(map['read']))
                deny_list  = '    '+'\n    '.join(sorted(map['deny']))

                msg = _('''
%(heading)s
Access map on '%(repos)s' for user '%(user)s'
%(heading)s
  * Writable:
%(write)s
%(sep)s
  * Readable:
%(read)s
%(sep)s
  * Denied:
%(deny)s
%(sep)s\n''') %  { 
                 'repos' : map['repos'], 
                 'user'  : map['user'], 
                 'heading' : '='*50, 
                 'sep'   : '-'*40, 
                 'write' : write_list, 
                 'read'  : read_list, 
                 'deny'  : deny_list, 
                }
            msgs.append(msg)
        return msgs


if __name__ == '__main__':
    import doctest
    doctest.testmod()
