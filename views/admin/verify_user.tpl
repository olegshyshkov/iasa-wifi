<!doctype html>
<html>
<head></head>
<body>

<a href="/administration">Админка</a>
<h1>Hello {{ username }}!</h1></body>

User group {{ group }}

<form action="/user/change_group" method="post">
<select name="group">
%for g in groups:
<option value="{{g}}">{{g}}</option>
%end
</select>
<input type="hidden" name="username" value="{{username}}">
<input type="submit" value="Change group">
</form>

<table border=1>
<tr><td></td><td>Old value</td><td>Current value</td>
%for v in params:
<tr>
	<td>{{v[0]}}</td>
	<td>{{v[1]}}</td>
	<td>{{v[2]}}</td>
</tr>
%end


</table>

<form action="/user/{{username}}" method="post">
	<input type="submit" value="Verify">
</form>

</html>
