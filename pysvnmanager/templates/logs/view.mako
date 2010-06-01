## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />
<%def name="head_tags()">
    <title>${_("Administration logs")}</title>
</%def>
<%def name="nav_bar()"></%def>
<%def name="ajax_script()"></%def>

<h2>${_("View history, revision")} ${c.log.get('revision')}</h2>

<textarea cols="80" rows="24">
${c.contents}
</textarea>

<form name="main_form" action="${h.url(controller="logs", action='rollback')}" onsubmit="return confirm('${_("Rollback to this revision, are you sure?")}');">
% if c.rollback_enabled:
  <input type="submit" name="submit" value='${_("Rollback to this revision")}'>
  &nbsp;&nbsp;&nbsp;&nbsp;
% endif
  <input type="button" name="close" value='${_("Close")}' onclick="window.close();">
</form>
