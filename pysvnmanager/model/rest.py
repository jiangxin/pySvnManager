#!/usr/bin/env python
# -*- coding: utf-8 -*-

from docutils import core
from docutils.writers.html4css1 import Writer,HTMLTranslator

class NoHeaderHTMLTranslator(HTMLTranslator):
    def __init__(self, document):
        HTMLTranslator.__init__(self,document)
        self.head_prefix = ['','','','','']
        self.body_prefix = []
        self.body_suffix = []
        self.stylesheet = []
    
    def astext(self):
        return ''.join(self.body)


_w = Writer()
_w.translator_class = NoHeaderHTMLTranslator

def reSTify(string):
    result = core.publish_string(string,writer=_w)
    if isinstance(result, basestring):
        result = unicode(result, 'utf-8')
    return result
