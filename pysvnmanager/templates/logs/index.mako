## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>${_("Administration logs")}</title>
</%def>

<SCRIPT LANGUAGE="JavaScript">
function paginate(num)
{
    showNoticesPopup();
    var params = {page:num};
    new Ajax.Updater(
    	{success:'logs',failure:'logs'}, 
    	'${h.url_for(action="paginate")}',
    	{asynchronous:true, evalScripts:true, method:'post', 
    		onComplete:
    			function(request)
    				{hideNoticesPopup();
    				new Effect.Highlight("logs",{duration:1});},
    		parameters:params});
}

</SCRIPT>

<h2>${_("Administration logs")}</h2>

<div id="logs">
${c.display}
</div>

