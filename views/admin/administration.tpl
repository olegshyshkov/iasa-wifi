<!doctype html>
<html>
<head></head>
<body>

<div>
    <a href="/account"> Account </a>
</div>

<table border = 1>
%for user in users:
	%if user.group.access:
		<tr bgcolor='#59F959'>
	%else:
		<tr bgcolor='red'>
	%end	
		<td><a href="/user/{{user['username']}}">  {{user.username}} 
			{{user.personal['firstname']}} {{user.personal['lastname']}}</a>
		</td>
		<td>
			%for dev in user['devices']:
				{{dev['mac']}}
			%end
		</td>
	</tr>
%end
</table>

</body>

</html>
