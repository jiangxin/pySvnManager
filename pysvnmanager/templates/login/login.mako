## -*- coding: utf-8 -*-
<h2>${_("Login")}</h2>
<form action=${h.url(controller="security", action='submit')} method="post">
${_("Username:")} <input type='text' name="username"><br>
${_("Password:")} <input type='password' name="password"><br>
<div>${c.login_message}</div>
<input type='submit' name='submit' value='${_("Login")}'>
<br>
</form>
