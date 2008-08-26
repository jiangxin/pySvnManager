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
        self.rcslog.log_per_page = cfg.log_per_page
    
    def __before__(self, action):
        super(LogsController, self).__before__(action)
        if not self.authz.is_super_user(self.login_as):
            return redirect_to(h.url_for(controller='security', action='failed'))
    
    def index(self):
        c.display = self.__get_log_display(1)
        return render('/logs/index.mako')

    def paginate(self):
        d = request.params
        page = int(d.get('page', '1'))
        return self.__get_log_display(page)

        
    def __get_log_display(self, current=1):
        logs = self.rcslog.get_page_logs(current)
        if not logs:
            return ""
        paginate = self.__get_paginate(current)
        
        buff  = '<div>%s</div>' % paginate
        buff +='''
<div>
<table>
<tr>
    <th>%(rev)s</th>
    <th>%(who)s</th>
    <th>%(when)s</th>
    <th>%(why)s</th>
    <th>%(comp)s</th>
</tr>''' % {'rev': _("Rev"), 
            'who': _("Who"), 
            'when': _("When"), 
            'why': _("Why"),
            'comp': _("Compare"),
            }
        
        for i in range(len(logs)-1, -1, -1):
            buff += '''
<tr>
    <td>%(rev)s</t>
    <td>%(who)s</td>
    <td>%(when)s</td>
    <td>%(why)s</td>
    <td>
        <input type="radio" name="left" value="%(rev)s">
        <input type="radio" name="right" value="%(rev)s">
    </td>
</tr>''' % {'rev' : logs[i].get('revision',''), 
            'who' : logs[i].get('author',''), 
            'when': logs[i].get('date',''), 
            'why' : h.link_to(logs[i].get('log',''), \
                              h.url(action='view', id=logs[i].get('revision','')), \
                              popup=['view_logs']
                              ), 
            }
        
        buff += '''
</table></div>
<div>%s</div>''' % paginate

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
        
        i=1
        while True:
            if i > total_page:
                break
            if i == current:
                buff += '%d%s' % (i, sep)
                i+=1
            elif i == 1 or i == total_page or i == current-1 or i == current+1:
                buff += '%s%s' % (link(i), sep)
                i+=1
            elif i < current-1:
                buff += '...%s' % sep
                i = current-1
            elif i > current+1:
                buff += '...%s' % sep
                i = total_page
            else:
                i+=1

        return buff 
    
    def compare(self):
        d = request.params
        left  = d.get('left', '')
        right = d.get('right', '')
        if not left or not right:
            return ""
        if left == right:
            return ""
        
        buff = '''<h2>%(title)s
<input type="radio" name="left" value="%(left)s">%(left)s
<input type="radio" name="right" value="%(right)s">%(right)s
</h2>
''' % {'title': _("Compares between"),
       'left' : left,
       'right': right}

        buff += "<pre>%s</pre>" % self.rcslog.differ(left, right)
        return buff


    def view(self, id):
        assert id and isinstance(id, basestring)
        c.contents = self.rcslog.cat(id)
        c.log = self.rcslog.get_logs(id, id)[0]
        if self.rcslog.head == id:
            c.rollback_enabled = True
        else:
            c.rollback_enabled = False
        return render('/logs/view.mako')
    
    def rollback(self, id):
        log_message = _("Rollback successfully to revision: %s") % id
        try:
            assert id and isinstance(id, basestring)
            self.rcslog.restore(id)
            self.rcslog.backup(comment=log_message, user=self.login_as)
        except Exception, e:
            msg = e.message
            if isinstance(msg, str):
                msg = unicode(msg, 'utf-8')
            c.msg = _("Rollback failed: %s") % msg
        else:
            c.msg = log_message

        return render('/logs/rollback.mako')
    