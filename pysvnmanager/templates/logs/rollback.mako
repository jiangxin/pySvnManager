## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />
<%def name="head_tags()">
    <title>${_("Administration logs")}</title>
</%def>
<%def name="nav_bar()"></%def>
<%def name="ajax_script()"></%def>

<h2>${_("Rollback")}</h2>

${c.msg}

<p>
<input type="button" value="${_('Close')}" onclick="window.close();">

