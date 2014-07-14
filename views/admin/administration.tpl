<!doctype html>
<html>
<head></head>
<body>

<div>
    <a href="/account"> Account </a>
</div>

<table border = 1>
%for user in users:
%if user['access']:
<tr bgcolor='#59F959'>
%else:
<tr bgcolor='red'>
%end
	<td>
		<form	action="/block_user" method="post">
		<input type="hidden" name="username" value="{{user['username']}}">
		<input type="hidden" name="access" value="{{user['access']}}">	
		%if user['access']:
			<input type="submit" value="Lock">
		%else:
			<input type="submit" value="Unlock">
		%end
		</form>

	</td>
	<td><a href="/user/{{user['username']}}">  {{user.personal['firstname']}} {{user.personal['lastname']}}</a>

		%for dev in user['devices']:
			{{dev['mac']}}
		%end
	</td>
</tr>


%end
</table>

</form>
</body>

</html>
