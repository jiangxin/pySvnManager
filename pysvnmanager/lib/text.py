# -*- coding: utf-8 -*-
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


import locale

def to_unicode(text, charset=None, escape=False):
    """Convert a `str` object to an `unicode` object.
    """
    utext = u''
    if not isinstance(text, str):
        if isinstance(text, Exception):
            # two possibilities for storing unicode strings in exception data:
            try:
                # custom __str__ method on the exception (e.g. PermissionError)
                utext = unicode(text)
            except UnicodeError:
                # unicode arguments given to the exception (e.g. parse_date)
                utext = ' '.join([to_unicode(arg, charset, False) for arg in text.args])
        else:
            utext = unicode(text)
    else:
        if charset:
            utext = unicode(text, charset, 'replace')
        else:
            try:
                utext = unicode(text, 'utf-8')
            except UnicodeError:
                utext = unicode(text, locale.getpreferredencoding(), 'replace')
    if escape:
        return utext.encode('raw_unicode_escape')
    else:
        return utext

def to_utf8(text, charset='gb18030', escape=False):
    """Convert a string to UTF-8, assuming the encoding is either UTF-8, ISO
    Latin-1, or as specified by the optional `charset` parameter.
    """
    utext = ''
    if isinstance(text, unicode):
        utext = text.encode('utf-8')
    elif not isinstance(text, str):
        utext = unicode(text).encode('utf-8')
    else:
        try:
            # Do nothing if it's already utf-8
            u = unicode(text, 'utf-8')
            utext = text
        except UnicodeError:
            try:
                # Use the user supplied charset if possible
                u = unicode(text, charset)
            except UnicodeError:
                # This should always work
                u = unicode(text, 'iso-8859-15')
            utext = u.encode('utf-8')
    if escape:
        return repr(utext)[1:-1]
    else:
        return utext

