## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="nav_bar()">
</%def>

<%def name="profile()">
  <div id="profile">
    <ul>
      <li>${h.link_to(_("Login"), h.url("login"))}</li>
    </ul>
  </div>
</%def>

<%def name="head_tags()">
    <title>${_("Login")}</title>
</%def>

<h2>${_("Login")}</h2>

<form action=${h.url(controller="security", action='submit')} method="post">
  <table class="hidden">
    <tr>
      <td>${_("Username:")}</td>
      <td><input type='text' name="username"></td></tr>
    <tr>
      <td>${_("Password:")}</td>
      <td><input type='password' name="password"></td></tr>
    <tr>
      <td colspan="2">${c.login_message}</td></tr>
    <tr>
      <td colspan="2" align="center"><input type='submit' name='submit' value='${_("Login")}'></td></tr>
  </table>
<br>
</form>
