## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>${_("Create repository")}</title>
</%def>

<h2>${_("Create repository")}</h2>

##<form name="main_form" method="post" action="${h.url_for(action="create_submit")}">
<%
    context.write( 
        h.form_remote_tag(
            html={'id':'main_form'}, 
            url=h.url_for(action='create_submit'), 
            update="message",
            method='post', before='showNoticesPopup()',
            complete='hideNoticesPopup();switch_message_box();',
        )
    )
%>
${_("Repository name:")}
	<input type="text" name="reposname" value="">
	<br>
    <input type="submit" name="submit" value="${_("Create repository")}">

</form>
