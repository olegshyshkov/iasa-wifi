<!doctype html>
<html>
<head></head>
<body>

<div id="header">
    <a href="/administration">Administation</a>
    <a href="/statistics">Statistics</a>
    <a href="/logout">Logout</a><br>
    <h1>Hello {{ username }}!</h1>
</div>


<div id="person" style="float:left; width: 30%">
<dl>
    <dd>Group: {{group}} </dd>
    <dd>Name: {{name}} </dd>
    <dd>Study group: {{study_group}}</dd>
</dl>
<a href="user/edit_profile">Edit profile</a>
</div>


<div id="devices" style="float:left; width: 70%">

<form action="account_new_device" method="post">
        Add device:
        <input name="mac" type="text"><br>
        <select name='type'>
            <option value='mobile phone'>mobile phone</option>
            <option value='tablet'>tablet</option>
            <option value='notebook'>notebook</option>
            <option value='other'>other</option>
        </select>
        <input type="submit" value="Add"><br><br>
</form>


%if devices:
Devices:
<table border="1">
    <tr><td>Mac</td><td>Type</td></tr>
    %for dev in devices:
    <tr>
        <td>{{ dev.mac }}</td>
        <td>{{ dev.typ }}</td>
    </tr>
    %end
</table>
%end
</div>
<br>
%if group == 'administrator':
Hello, Johny!
%end

</body>
</html>
