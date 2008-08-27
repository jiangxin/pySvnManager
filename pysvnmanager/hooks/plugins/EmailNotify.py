#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pysvnmanager.hooks.plugins import *
from pysvnmanager.hooks.plugins import _

class EmailNotify(PluginBase):

    # Plugin id
    id = __name__.rsplit('.',1)[-1]
    
    # Brief name for this plugin.
    name = _("Send email notify for commit event")
    
    # Both description and detail are reStructuredText format. 
    # Reference about reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html

    # Short description for this plugin.
    description = _("Send a notification email describing either a commit or "
                    "a revprop-change action on a Subversion repository.")
    
    # Long description for this plugin.
    detail = _("""
You must provide proper options to commit-email.pl using the
configuration form for this plugin.

You can simply just provide the email_addr as the options.

  [options] email_addr [email_addr ...]

But to be more versitile, you can setup a path-based email 
notifier.

  [-m regex1] [options] [email_addr ...]
  [-m regex2] [options] [email_addr ...] 
  ...

Options:

-m regex              Regular expression to match committed path
--from email_address  Email address for 'From:' (overrides -h)
-r email_address      Email address for 'Reply-To:
-s subject_prefix     Subject line prefix
--diff n              Do not include diff in message (default: y)
""")
    
    # Hooks-plugin type: T_START_COMMIT, ..., T_POST_UNLOCK
    type = T_POST_COMMIT
    
    # Plugin config option/value in config ini file.
    # email_notify_enable = yes|no
    # email_notify_config = -m "." --diff y --from <from@addr> -r <reply@addr> -s "[prefix]" to@addr
    key_switch = "email_notify_enable"
    key_config = "email_notify_config"
    
    def enabled(self):
        """
        Return True, if this plugin has been installed.
        Simply call 'has_config()'.
        """
        return self.has_config(self.key_switch) and self.has_config(self.key_config)
    
    def install_info(self):
        """
        Show configurations if plugin is already installed.
        
        return reStructuredText.
        reST reference: http://docutils.sourceforge.net/docs/user/rst/quickref.html
        """
        result = self.description
        if self.enabled():
            result += "\n\n"
            result += "**Current configuration**\n\n"
            if self.get_config(self.key_switch) == "yes":
                result += _("- Email notify enabled.")
            else:
                result += _("- Email notify disabled.")
            result += "\n"
            result += _("- Parameters: ``") + self.get_config(self.key_config) + '``'
                
        return result
    
    def install_config_form(self):
        """
        This method will be called to build setup configuration form.
        If this plugin needs parameters, provides form fields here.
        Any html and javascript are welcome.
        """
        if self.get_config(self.key_switch)=="yes":
            enable_checked  = "checked"
            disable_checked = ""
        else:
            enable_checked  = ""
            disable_checked = "checked"

        result = ""
        result += "<p><strong>%s</strong></p>" % _("Fill this form")
        result += "<blockquote>"
        result += _("Enable email notify.")
        result += "<input type='radio' name='switch' value='yes' " + \
                enable_checked  + ">" + _("Enable") + "&nbsp;"
        result += "<input type='radio' name='switch' value='no' " + \
                disable_checked + ">" + _("Disable") + "<br>"
        result += _("Input email notify configurations: ") + \
                "<input type='text' name='config' size='64' value='%s'>" % \
                self.get_config(self.key_config)
        result += "</blockquote>"
        return result
        
    def uninstall(self):
        """
        Uninstall hooks-plugin from repository.
        Simply call 'unset_config()' and 'save()'.
        """
        self.unset_config(self.key_config)
        self.unset_config(self.key_switch)
        self.save()
    
    def install(self, params=None):
        """
        Install hooks-plugin from repository.
        Simply call 'set_config()' and 'save()'.
        
        Form fields in setup_config() will pass as params.
        """
        switch = params.get('switch', 'yes')
        if switch != 'yes':
            switch = 'no'
        config = params.get('config')
        if not config:
            raise Exception, _("Wrong configuration.")
        self.set_config(self.key_switch, switch)
        self.set_config(self.key_config, config)
        self.save()
        
def execute(repospath=""):
    """
    Generate and return a hooks plugin object

    @param request: repos full path
    @rtype: Plugin
    @return: Plugin object
    """
    return EmailNotify(repospath)
