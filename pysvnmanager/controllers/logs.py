import logging

from pysvnmanager.lib.base import *
from pysvnmanager.model import rcsbackup as _rcs
from pysvnmanager.model.svnauthz import *

log = logging.getLogger(__name__)

class LogsController(BaseController):
    requires_auth = True
    
    def __init__(self):
        self.authz = SvnAuthz(cfg.authz_file)
        self.login_as = session.get('user')
        self.rcslog = _rcs.RcsLog(cfg.authz_file)
        # Default logs per page is 10
        #self.rcslog.log_per_page = 10

    def __auth_failed(self):
        if self.authz.is_super_user(self.login_as):
            return False
        else:
            return True
    
    def index(self):
        if self.__auth_failed():
            return render('/auth_failed.mako')
        
        c.display = self.__get_log_display(1)
        return render('/logs/index.mako')

    def paginate(self):
        if self.__auth_failed():
            return render('/auth_failed.mako')
        
        d = request.params
        page = int(d.get('page', '1'))
        return self.__get_log_display(page)

        
    def __get_log_display(self, current=1):
        logs = self.rcslog.get_page_logs(current)
        if not logs:
            return ""
        paginate = self.__get_paginate(current)
        
        buff  = '<span>%s</span>' % paginate
        buff +='''
<table>
<tr>
    <th>%(rev)s</th>
    <th>%(who)s</th>
    <th>%(when)s</th>
    <th>%(why)s</th>
</tr>''' % {'rev': _("Rev"), 
            'who': _("Who"), 
            'when': _("When"), 
            'why': _("Why"),}
        
        for i in range(len(logs)-1, -1, -1):
            buff += '''
<tr>
    <td>%(rev)s</t>
    <td>%(who)s</td>
    <td>%(when)s</td>
    <td>%(why)s</td>
</tr>''' % {'rev' : logs[i].get('revision',''), 
            'who' : logs[i].get('author',''), 
            'when': logs[i].get('date',''), 
            'why' : logs[i].get('log',''), }
        
        buff += '''
<span>%s</span>
</table>''' % paginate

        return buff
    
    def __get_paginate(self, current=1):
        def link(i):
            return '<a href="#" onclick="paginate(%d)">%d</a>' % (i,i)
        
        total_page = self.rcslog.total_page
        if total_page < 2:
            return ""

        if current < 1:
            current = 1
        if current > total_page:
            current = total_page
        
        sep = " "
        buff = _("Page: ")
        for i in range(1, total_page+1):
            if i == current:
                buff += '%d%s' % (i, sep)
            elif i == 1 or i == total_page or i == current-1 or i == current+1:
                buff += '%s%s' % (link(i), sep)
            elif i < current-1:
                buff += '...'
                i = current-1
            elif i > current+1:
                buff += '...'
                i = total_page

        return buff 