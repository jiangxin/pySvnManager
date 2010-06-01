## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>${_("Create repository")}</title>
</%def>

<h2>${_("Create repository")}</h2>

##<form name="main_form" method="post" action="${h.url(controller="repos", action="create_submit")}">

<form action="${h.url(controller="repos", action='create_submit')}"
  id="main_form" method="POST"
  onsubmit="showNoticesPopup();
            new Ajax.Updater('message',
                             '${h.url(controller="repos", action='create_submit')}',
                             {asynchronous:true, evalScripts:true, method:'post',
                              onComplete:function(request){hideNoticesPopup();switch_message_box();},
                              parameters:Form.serialize(this)});
            return false;">

${_("Repository name:")}
	<input type="text" name="reposname" value="">
	<br>
    <input type="submit" name="submit" value="${_("Create repository")}">

</form>
