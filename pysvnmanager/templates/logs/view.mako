## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>${_("Administration logs")}</title>
</%def>

<SCRIPT LANGUAGE="JavaScript">
function rollback()
{
  
}

</SCRIPT>

<h2>${_("View history, revision")} ${c.log.get('revision')}</h2>

<textarea cols="80" rows="24">
${c.contents}
</textarea>

<form name="main_form" action="${h.url_for(action='rollback')}">
<input type="submit" name="submit" value='${_("Rollback to this revision")}'>
</form>