#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pysvnmanager.hooks.plugins import PluginBase

class EolStyleCheck(PluginBase):
    name = "mime-type and eol-style check"
    description = "New file must provide svn:eol-style if not binary file."
    option = "check_eol_style"
    value = "yes"
    
    def is_set(self):
        return self.get_config(self.option) == self.value
    
    def show(self):
        return self.description
    
    def show_form(self):
        return self.description
        
    def delete_plugin(self):
        self.del_config(self.option)
        self.write()
    
    def set_plugin(self, form=None):
        self.set_config(self.option, self.value)
        self.write()
        
def execute(repospath=""):
    """
    Generate and return a hooks plugin object

    @param request: repos full path
    @rtype: Plugin
    @return: Plugin object
    """
    return EolStyleCheck(repospath)