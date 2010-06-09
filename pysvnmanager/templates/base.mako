# -*- coding: utf-8 -*-
<html>
  <head>
    ${self.head_tags()}
    ${self.ajax_script()}
    ${h.stylesheet_link(h.url('/css/common.css'), media='all')}

    <SCRIPT LANGUAGE="JavaScript">
<%
msg = ''
if hasattr(c, "global_message"):
    msg += "var global_message = \"%s\";\n" % c.global_message
else:
    msg += "var global_message = \"\";\n"
context.write(msg)
%>
    function showGlobalMessage()
    {
      if (global_message) {
          info_msg(global_message);
      }
    }
    </SCRIPT>
  </head>
  <body ${self.body_params()}>

    <div id="popup_shadow" style="z-index:100;visibility:hidden;display:none;position:absolute;top:0px;left:0px;width:100%;height:100%;background:#000000;opacity:0.0;filter:alpha(opacity=0);"></div>
    <div id="popup_notices" style="z-index:101;border:1px solid gray;position:absolute;top:0;left:250px;visibility:hidden;display:none;background:#eeee20;">
       ${_("Loading, please wait...")}
    </div>

    <div class="header">
	    ${self.nav_bar()}
	    ${self.profile()}
    </div>

    <div id="message_box" style="visibility:hidden;position:absolute; margin:1em;" class=gainlayout>
      <div id="message"></div>
      &nbsp;&nbsp;&nbsp;&nbsp;
      <a class="clear-link" href="#"
         onClick="document.getElementById('message').innerHTML='';switch_message_box()"
         >${_("Clear message")}</a>
    </div>
	
    <div class="page">
      ${next.body()}
    </div>

    <div class="footer">
      <% context.write( _("Powered by <a href=\"%(url1)s\">pySvnManager</a> &copy; 2008-2010 <a href=\"%(url2)s\">ossxp.com</a>") % {"url1": "http://pysvnmanager.sourceforge.net", "url2":"http://www.ossxp.com/"} ) %>
    </div>
  </body>
</html>

<%def name="head_tags()">
    <title>Override Me!</title>
</%def>

<%def name="nav_bar()">
  <div id="menu">
    <ul>
      <% class_name = c.menu_active == "check" and "selected" or "unselected" %>
      <li>${h.link_to(_("Check permissions"), h.url(controller="check",action="index"), Class=class_name)}</li>
      <% class_name = c.menu_active == "role" and "selected" or "unselected" %>
      <li>${h.link_to(_("Role management"), h.url(controller="role",action="index"), Class=class_name)}</li>
      <% class_name = c.menu_active == "authz" and "selected" or "unselected" %>
      <li>${h.link_to(_("ACL management"), h.url(controller="authz",action="index"), Class=class_name)}</li>
      <% class_name = c.menu_active == "repos" and "selected" or "unselected" %>
      <li>${h.link_to(_("Repos management"), h.url(controller="repos",action="index"), Class=class_name)}</li>
      <% class_name = c.menu_active == "logs" and "selected" or "unselected" %>
      <li>${h.link_to(_("Change log"), h.url(controller="logs",action="index"), Class=class_name)}</li>
      <li><em>${h.link_to(_("Help"), "http://www.ossxp.com/doc/pysvnmanager/", target="_blank")}</em></li>
    </ul>
  </div>
</%def>

<%def name="profile()">
  <div id="profile">
    <ul>
      <li>${_("Welcome")} ${session.get('user')}</li>
      <li>${h.link_to(_("Logout"), h.url("logout"))}</li>
    </ul>
  </div>
</%def>

<%def name="ajax_script()">
${h.javascript_link(h.url('/javascripts/prototype.js'))}
${h.javascript_link(h.url('/javascripts/scriptaculous.js'))}
${h.javascript_link(h.url('/javascripts/unittest.js'))}

<!-- IE layout bugfix -->
<!--[if lt IE 7]><style>
.gainlayout { height: 0; }
</style><![endif]-->

<!--[if IE 7]><style>
.gainlayout { zoom: 1;}
</style><![endif]-->

<script language='javascript'>
function getWinWidth()
{
    var winW = 630;

    if (parseInt(navigator.appVersion)>3) {
        if (navigator.appName=="Netscape") {
            winW = window.innerWidth;
        }
        if (navigator.appName.indexOf("Microsoft")!=-1) {
            winW = document.body.offsetWidth;
        }
    }
    return winW;
}
function getWinHeight()
{
    var winH = 460;

    if (parseInt(navigator.appVersion)>3) {
        if (navigator.appName=="Netscape") {
            winH = window.innerHeight;
        }
        if (navigator.appName.indexOf("Microsoft")!=-1) {
            winH = document.body.offsetHeight;
        }
    }
    return winH;
}
</script>

<script language='javascript'>
function showPopupShadow()
{
  document.getElementById('popup_shadow').style.visibility = 'visible';
  document.getElementById('popup_shadow').style.display = 'inline';
}

function hidePopupShadow()
{
  document.getElementById('popup_shadow').style.visibility = 'hidden';
  document.getElementById('popup_shadow').style.display = 'none';
}

function showNoticesPopup()
{
  showPopupShadow();

  document.getElementById('popup_notices').style.top= '0px';
  document.getElementById('popup_notices').style.left= getWinWidth()/2+'px';
  document.getElementById('popup_notices').style.visibility = 'visible';
  document.getElementById('popup_notices').style.display = 'inline';
}

function hideNoticesPopup()
{
  hidePopupShadow();

  document.getElementById('popup_notices').style.visibility = 'hidden';
  document.getElementById('popup_notices').style.display = 'none';
}

function warn_msg(message)
{
	set_message_box("<div class='warning'>"+message+"<div>");
}

function error_msg(message)
{
	set_message_box("<div class='error'>"+message+"<div>");
}

function info_msg(message)
{
	set_message_box("<div class='info'>"+message+"<div>");
}

function set_message_box(message)
{
	document.getElementById('message').innerHTML=message;
	switch_message_box();
}

function switch_message_box()
{
	c=document.getElementById('message').innerHTML;
	s=document.getElementById('message_box').style;
	if (c)
	{
		s.visibility='visible';
		s.position = 'relative';
	}
	else
	{
		s.visibility='hidden';
		s.position = 'absolute';
	}
}
</script>
</%def>

<%def name="body_params()"> onload="showGlobalMessage()" </%def>
