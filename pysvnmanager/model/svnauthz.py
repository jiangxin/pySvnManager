#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Subversion authz config file management.

Basic classes used for Subversion authz management.
"""

from configobj import ConfigObj
import re
import sys
import logging
log = logging.getLogger(__name__)

# i18n works only as pysvnmanager (a pylons app) model.
from pylons import config
if config.get('package') and not config.has_key('unittest'):
    from pylons.i18n import _
else:
    def _(message): return message

reload(sys) # in Python2.5, method sys.setdefaultencoding 
            #will be delete after initialize. we need reload it.
sys.setdefaultencoding('utf-8')

RIGHTS_W = 4
RIGHTS_R = 2
RIGHTS_NONE = 0
RIGHTS_RW = RIGHTS_R | RIGHTS_W
RIGHTS_ALL = RIGHTS_R | RIGHTS_W

def is_valide_name(name, type=""):
    msg = ''
    if type == 'repos':
        bad_chars = r'''[,\s!\\'"]'''
    else:
        bad_chars = r'''[,\s!\\/'"]'''
        
    if not name:
        msg = _("Name is not given.")
    elif not isinstance(name, basestring):
        msg = _("Name is not string.")
    else:
        p = re.compile(bad_chars)
        if p.search(name):
            msg = _("Name contains invalid characters.")
    return msg

def normalize_user(name):
    if isinstance(name, basestring):
        name = name.strip()
    return name

def normalize_repos(name):
    if isinstance(name, basestring):
        name = name.strip()
        name = name.strip('/')
    if not name:
        name = '/'
    return name

def normalize_path(name):
    if isinstance(name, basestring):
        name = name.strip()
        name = name.strip('/')
    if not name:
        name = '/'
    elif isinstance(name, basestring) and name[0] != '/':
        name = '/'+name
        
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

    def __init__(self, name, realname='', email=''):
        name = name.strip()
        realname = realname.strip()
        email = email.strip()

        if not name:
            raise Exception, 'Username is not provided'

        self.__name = name
        self.__realname = realname
        self.__email = email

    def __get_unique_name__(self):
        return self.__name

    uname = property(__get_unique_name__)
    name  = property(__get_unique_name__)

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
            obj = obj.strip()
        else:
            return False

        if not obj:
            return False

        return obj.lower() == self.uname.lower()


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
    >>> str(a)
    'aliasname = username'
    >>> user in a
    True
    >>> user = User('jiangxin')
    >>> a.user = user
    >>> str(a)
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
    >>> str(a)
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

        aliasname = aliasname.strip()

        if not aliasname:
            raise Exception, _('Aliasname is not provided.')
        elif aliasname and aliasname[0]=='&':
            raise Exception, _('Aliasname should not begin with &.')

        self.__name = aliasname
        self.__userobj = userobj


    def __get_name__(self):
        if self.__name:
            return self.__name
        else:
            return ''

    name = property(__get_name__)
    aliasname = property(__get_name__)

    def __get_unique_name__(self):
        if self.__name:
            return '&'+self.__name
        else:
            return ''

    uname = property(__get_unique_name__)

    def __get_username__(self):
        if self.__userobj:
            return self.__userobj.name
        else:
            return ''

    username = property(__get_username__)

    def __get_user__(self):
        return self.__userobj.name

    def __set_user__(self, userobj):
        if not isinstance(userobj, object):
            raise Exception, 'Wrong parameter for userobj.'
        self.__userobj = userobj

    user = property(__get_user__, __set_user__)

    def __str__(self):
        return "%s = %s" % (self.name, self.username)

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
            obj = obj.strip()

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
        name = name.strip()

        if not name:
            raise Exception, _('Group name is not provided.')
        elif name and name[0]=='@':
            raise Exception, _('Group name should not begin with @.')

        self.name = name
        self.__members = []

    def __get_unique_name__(self):
        if self.name:
            if self.name[0] != '$' and self.name != '*':
                return '@'+self.name
            else:
                return self.name
        else:
            return ''

    uname = property(__get_unique_name__)

    def __get_member_names__(self):
        if self.__members:
            return map(lambda x: x.uname, self.__members)
        else:
            return []

    membernames = property(__get_member_names__)

    def __get_member_objs__(self):
        return self.__members

    memberobjs = property(__get_member_objs__)

    def __str__(self):
        if self.name[0] != '$' and self.name != '*':
            return "%s = %s" % (self.name, ', '.join(sorted(self.membernames)))
        else:
            return "# Built-in group: %s" % self.name

    def __iter__(self):
        for i in self.__members:
            yield i
    
    def __valid_group__(self, groupobj, checked_groups=None):
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
            if not self.__valid_group__(member, checked_groups):
                return False
            # Remove group to hash of checked groups. 
            # Other group members may contain this group
            checked_groups.remove(member)
        return True

    def append(self, member, autodrop=False):
        if isinstance(member, (list, tuple)):
            for i in member:
                self.append(i, autodrop)
            return True
        if not member in self.__members:
            self.__members.append(member)
            if not self.__valid_group__(self):
                self.__members.remove(member)
                if not autodrop:
                    raise Exception, _('Recursive group membership for %s') \
                        % member.uname
        return True

    def remove(self, members):
        ulist = []
        if isinstance(members, (str, unicode)):
            for user in members.split(','):
                if user.strip():
                    ulist.append(user.strip())
        elif isinstance(members, (list, tuple)):
            ulist.extend(members)
        for user in ulist:
            if isinstance(user, (str, unicode)):
                mlist = map(lambda x: x.uname, self.__members)
                if user not in mlist:
                    continue
                del self.__members[mlist.index(user)]
            else:
                self.__members.remove(user)

        return True

    def remove_all(self):
        self.__members = []

    def __cmp__(self, obj):
        """For list sorting"""
        if isinstance(obj, Group):
            return cmp(self.uname, obj.uname)
        else:
            return -1

    def __contains__(self, obj):
        if not obj: 
            obj = '*'

        if isinstance(obj, Alias):
            if self.__contains__(obj.username):
                return True
            obj = obj.uname
        elif isinstance(obj, (User, Group)):
            obj = obj.uname
        elif isinstance(obj, (str, unicode)):
            obj = obj.strip()
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
        self.user_list = []

    def __iter__(self):
        for i in self.user_list:
            yield i

    def get(self, name):
        return self.get_or_set(name, autocreate=False)

    def get_or_set(self, name, autocreate = True):
        if isinstance(name, User):
            return name
        
        name = normalize_user(name)
        if not name:
            return None
        if name[0] == '&' or name[0] == '@' or name[0] == '$':
            raise Exception, _("Not a valide username: %s") % name

        for user in self.user_list:
            if user.name == name:
                return user

        msg = is_valide_name(name)
        if msg:
            raise Exception, msg

        if autocreate:
            user = User(name)
            self.user_list.append(user)
            return user
        else:
            return None


class AliasList(object):
    """Store all alias objects defined by [aliases] section or referenced in 
    [group], [repos:/path/to] but not be set.
    """
    def __init__(self):
        self.alias_list = []

    def __iter__(self):
        for i in self.alias_list:
            yield i

    def get(self, name):
        return self.get_or_set(name, False)

    def get_or_set(self, name, autocreate = True):
        if isinstance(name, Alias):
            return name
        
        name = normalize_user(name)
        if not name:
            return None
        if name[0] == '&':
            name = name[1:]
        for alias in self.alias_list:
            if alias.aliasname == name:
                return alias

        msg = is_valide_name(name)
        if msg:
            raise Exception, msg

        if autocreate:
            alias = Alias(name)
            self.alias_list.append(alias)
            return alias
        else:
            return None

    def remove(self, name):
        if isinstance(name, (str, unicode)):
            alias = self.get(name.strip())
        else:
            alias = name
        if alias:
            self.alias_list.remove(alias)
            return True
        else:
            return False

    def __str__(self):
        buff = "[aliases]\n"
        for alias in sorted(self.alias_list):
            buff += unicode(alias)
            buff += '\n'
        return buff


class GroupList(object):
    """Store all group objects defined by [group] section or referenced in 
    [group], [repos:/path/to] but not be set.
    """
    def __init__(self):
        self.group_list = []

    def __iter__(self):
        for i in self.group_list:
            yield i

    def get(self, name):
        return self.get_or_set(name, False)

    def get_or_set(self, name, autocreate = True):
        if isinstance(name, Group):
            return name
        
        name = normalize_user(name)
        if not name:
            return None
        if name[0] == '@':
            name = name[1:]
        for group in self.group_list:
            if group.name == name:
                return group

        msg = is_valide_name(name)
        if msg:
            raise Exception, msg

        if autocreate:
            group = Group(name)
            self.group_list.append(group)
            return group
        else:
            return None

    def remove(self, name, force=False):
        name = name.strip()
        item = self.get(name)
        if item:
            for group in self.group_list:
                if group == item:
                    continue
                if item in group.memberobjs:
                    if force:
                        group.memberobjs.remove(item)
                    else:
                        raise Exception, \
                                _('Group %s is referenced by group %s.') \
                                % (name, group.uname)
            self.group_list.remove(item)
            return True
        else:
            return False

    def __str__(self):
        buff = "[groups]\n"
        for group in sorted(self.group_list):
            if group.name[0] != '$' and group.name != '*':
                buff += unicode(group)
                buff += '\n'
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

    def __get_unique_name__(self):
        return self.userobj.uname

    uname = property(__get_unique_name__)

    def __set_rights__(self, rights):
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

    def __get_rights__(self):
        return self.__rights

    rights = property(__get_rights__, __set_rights__)

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
        rstr = ''
        rbit = self.__rights
        if rbit & RIGHTS_R:
            rstr += 'r'
        if rbit & RIGHTS_W:
            rstr += 'w'
        return "%s = %s" % (self.userobj.uname, rstr)

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
    
    def __get_fullame__(self):
        return self.repos+':'+self.path

    fullname = property(__get_fullame__)

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
            user = user.strip()

            if user in unamelist:
                del self.__rule_list[unamelist.index(user)]

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
            return ''
        if self.repos == '/' or not self.repos:
            buff = "[%s]\n" % self.path
        else:
            buff = "[%s:%s]\n" % (self.repos, self.path)
        for rule in sorted(self.__rule_list):
            tmp = unicode(rule)
            if tmp:
                buff += tmp
                buff += '\n'
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
        name = name.strip()
        self.__repos_name = name
        self.__admins = []
        self.module_list = []
        self.authz = ''

    def __iter__(self):
        for i in self.module_list:
            yield i
    
    def __get_name__(self):
        return self.__repos_name

    def __set_name__(self, name):
        self.__repos_name = name.strip()

    name = property(__get_name__, __set_name__)

    def __get_path_list(self):
        return map(lambda x:x.path, self.module_list)
    
    path_list = property(__get_path_list)

    def __get_admins(self):
        alist = [i.uname for i in self.__admins]
        return ', '.join(sorted(alist))

    def __set_admins(self, admins):
        self.__admins = []
        return self.add_admin(admins)
    
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
    
    admins = property(__get_admins, __set_admins)
    
    def add_module(self, path):
        path = normalize_path(path)

        for i in self.module_list:
            if i.path == path:
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
        return True

    def get_module(self, path):
        path = normalize_path(path)

        for i in self.module_list:
            if i.path == path:
                return i
        return None

    def is_blank(self):
        if self.__admins or self.module_list:
            return False
        else:
            return True

    def __str__(self):
        buff = ''
        for i in sorted(self.module_list):
            tmp = unicode(i)
            if tmp:
                buff += tmp
                buff += '\n'
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

    def __iter__(self):
        for i in self.repos_list:
            yield i

    def get(self, name):
        return self.get_or_set(name, False)

    def get_or_set(self, name, autocreate = True):
        if isinstance(name, Repos):
            return name
        
        name = normalize_repos(name)

        for repos in self.repos_list:
            if repos.name == name:
                return repos

        msg = is_valide_name(name, 'repos')
        if msg:
            raise Exception, msg

        if autocreate:
            repos = Repos(name)
            self.repos_list.append(repos)
            return repos
        else:
            return None

    def remove(self, name, recursive=False):
        name = normalize_repos(name)

        if name == '/' and not recursive:
            return False

        rlist = map(lambda x: x.name, self.repos_list)
        try:
            idx = rlist.index(name)
        except:
            raise Exception, "Repos '%s' not exist" % name

        repos = self.repos_list[idx]
        assert(repos.name == name)

        if recursive:
            if name == '/':
                self.repos_list[idx].del_all_modules()
                return True
            else:
                del self.repos_list[idx]
                return True

        if repos.is_blank():
            del self.repos_list[idx]
            return True
        else:
            return False

    def __str__(self):
        buff = ''
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
        self.__userlist  = UserList()
        self.__aliaslist = AliasList()
        self.__grouplist = GroupList()
        self.__reposlist = ReposList()
        self.__version = '0.1.0'
        self.config = None
        self.add_repos('/')
        if fileobj:
            self.load(fileobj)

    def __get_userlist__(self):
        return self.__userlist

    userlist = property(__get_userlist__)

    def __get_aliaslist__(self):
        return self.__aliaslist

    aliaslist = property(__get_aliaslist__)

    def __get_grouplist__(self):
        return self.__grouplist

    grouplist = property(__get_grouplist__)

    def __get_reposlist__(self):
        return self.__reposlist

    reposlist = property(__get_reposlist__)

    def __get_version(self):
        return self.__version
    
    version = property(__get_version)
    
    def update_revision(self):
        if not self.__version:
            return
        major, minor = self.__version.rsplit('.',1)
        if minor.isdigit():
            rev = int(minor)+1
        else:
            rev = 0
        self.__version = "%s.%d" % (major, rev)
        
    def modulelist(self, reposobj=None):
        if reposobj:
            for i in reposobj.module_list:
                yield i 
        else:
            for i in self.reposlist:
                for j in i.module_list:
                    yield j

    def rulelist(self, module=None):
        if module:
            for i in module:
                yield i
        else:
            for i in self.reposlist:
                for j in i.module_list:
                    for k in j:
                        yield k

    def load(self, fileobj):
        '''
        Initial SvnAuthz from authz file.
        file can be filename, or file handler, StingIO,...
        '''
        if not fileobj:
            return

        # set encoding to 'utf8'
        self.config = ConfigObj(fileobj, encoding='utf8', default_encoding='utf8')
        if not self.config:
            return

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

    def save(self, revision):
        filename = self.config.filename
        
        if not revision:
            revision = self.version
        last_rev = self.get_revision_from_file(filename)
        log.debug("this revision: %s, last: %s" % (revision, last_rev))
        if last_rev and revision != last_rev:
            raise Exception, _("Update failed! You are working on a out-of-date revision.") + " (%s <> %s)" % (revision, last_rev)

        self.update_revision()        
        f = open(filename, 'w')
        f.write(unicode(self))
        f.close()
        
    def __str__(self):
        buff = ""
        buff += self.compose_version()
        buff += self.compose_acl()
        buff += '\n'
        buff += unicode(self.__grouplist)
        buff += '\n'
        buff += unicode(self.__aliaslist)
        buff += '\n'
        buff += unicode(self.__reposlist)
        return buff

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

        reposname = reposname.strip()
        path = path.strip()

        self.add_rules(reposname, path, contents, force=True)

    def parse_aliases(self, aliases):
        for (name, username) in aliases.items():
            name = name.strip()
            username = username.strip()
            self.add_alias(name, username)

    def parse_acl(self):
        acls = self.config.initial_comment
        pattern = re.compile(r'^#\s*admin\s*:\s*(.+?)\s*=\s*(.+?)\s*(?:#.*)?$')
        if acls:
            for acl in acls:
                i = pattern.search(acl)
                if i:
                    name  = i.group(1).strip()
                    admin = i.group(2).strip()
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

    def get_revision_from_file(self, filename=None):
        if not filename:
            filename = self.config.filename
        pattern = re.compile(r'^#\s*version\s*[:=]\s*(.+?)\s*(?:#.*)?$')
        version = ""
        f = open(filename)
        for line in f:
            i = pattern.search(line)
            if i:
                version  = i.group(1)
                break
        return version
            
        
    def compose_version(self):
        if self.__version:
            buff = "# version : %s\n" % self.__version
        else:
            buff = ""
        return buff

    def compose_acl(self):
        buff = ""
        for repos in self.__reposlist:
            admins = repos.admins
            if admins:
                buff += "# admin : %s = %s\n" % (repos.name, admins)
        return buff

    def is_admin(self, user, repos='/', admins=None):
        if isinstance(user, User):
            user = user.uname
        elif isinstance(user, Alias):
            user = user.username
        elif not user:
            return False

        repos = self.__reposlist.get(repos)
        
        if repos:
            if admins is None:
                admins = repos.admins
            for i in admins.split(','):
                if i: i = i.strip()
                
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
            if force:
                module = self.add_module(reposname, path)
            else:
                raise Exception, _('No module exist for %s:%s') % (reposname, path)

        if reset:
            module.clean_rules()

        return self.add_rules(reposname, path, rules, force=force)
 
    def get_userobj(self, name, autocreate=False):
        name = normalize_user(name)

        if not name:
            return None
        if name[0] == '@' or name[0] == '$' or name == '*':
            obj = self.__grouplist.get_or_set(name, autocreate = autocreate)
        elif name[0] == '&':
            obj = self.__aliaslist.get_or_set(name, autocreate = autocreate)
        else:
            obj = self.__userlist.get_or_set(name, autocreate = autocreate)
        return obj

    def get_manageable_repos_list(self, username):
        repos_list = []
        if self.is_admin(username, '/'):
            repos_list.extend(map(lambda x:x.name, self.reposlist))
        else:
            for i in self.reposlist:
                if self.is_admin(username, i):
                    repos_list.append(i.name)
        return repos_list
        
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

    def update_group(self, name, members, autodrop=False):
        group = self.__grouplist.get_or_set(name)
        group.remove_all()
        if members:
            return self.add_group_member(group, members, autodrop=autodrop)
        return group

    def del_group(self, name, force=False):
        if not self.chk_grp_ref_by_rules(name):
            return self.__grouplist.remove(name, force=force)
        return False

    def add_group_member(self, group, members, autodrop=False):
        groupobj = self.__grouplist.get_or_set(group)

        ulist = []
        if isinstance(members, (str, unicode)):
            for user in members.split(','):
                user = user.strip()
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
        userobj = self.__userlist.get_or_set(username)
        return userobj

    def add_alias(self, aliasname, username=None):
        alias = self.__aliaslist.get_or_set(aliasname)
        if not alias:
            return None

        userobj = self.__userlist.get_or_set(username)
        alias.user = userobj

        return alias

    def del_alias(self, name, force=False):
        name = name.strip()

        alias = self.__aliaslist.get(name)
        if not alias:
            return False

        if self.chk_alias_ref_by_rules(alias):
            raise Exception, _('Alias %s is used by rules.') % alias.uname

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
        if not name:
            return False

        if isinstance(name, (User, Group, Alias)):
            name = name.uname

        for i in self.modulelist():
            ulist = map(lambda x:x.uname, self.rulelist(i))
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
        self.__check_ref_by_rules(name)

    def check_rights(self, user, repos, path, required):
        if isinstance(user, (str, unicode)):
            user = user.strip()
        if isinstance(repos, (str, unicode)):
            repos = repos.strip()
        if isinstance(path, (str, unicode)):
            path  = path.strip().rstrip('/')

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
        if isinstance(user, (str, unicode)):
            user = user.strip()
        if not user:
            user = '*'
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
            user = user.strip()
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
            user = user.strip()
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
            user = user.strip()
        if not user:
            user = '*'

        if isinstance(reposname, basestring):
            reposname = normalize_repos(reposname)

        maps = []
        msgs = []
        if not reposname or reposname=='*' or reposname=='...':
            for i in sorted(self.__reposlist):
                map = self.get_access_map(user, i.name, descend=False)
                if map:
                    map['user'] = unicode(user)
                    map['repos'] = i.name
                    maps.append(map)
        elif isinstance(reposname, (list, tuple)):
            for i in reposname:
                map = self.get_access_map(user, i, descend=False)
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

    def show_access_map(self, user='*', reposname=None, abbr=False):
        msgs = self.get_access_map_msgs(user, reposname, abbr=abbr)
        for msg in msgs:
            print msg

    def get_repos_path_list(self, reposname, descend=True):
        plist = set()
        repos = self.get_repos(reposname)
        if repos:
            plist = set(repos.path_list)
            
        if descend and (repos==None or repos.name != '/'):
            repos = self.get_repos('/')
            if repos:
                plist = plist.union(set(repos.path_list))
        return sorted(plist)


if __name__ == '__main__':
	#sys.exit(main())
    import doctest
    doctest.testmod()
