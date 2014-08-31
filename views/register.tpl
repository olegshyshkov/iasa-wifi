<!doctype html>
<html>
<head></head>
<body>

<ul>
%for e in errors:
 <li>{{e}}</li>
%end
</ul>

<script type="text/javascript">
function validateForm() (argument) {
    return false;
}
</script>


<form method="post" action="/user/save" onsubmit="return validateForm()">
<dl>
    <dt>Login:</dt>
        <dd><input type="text" name="username" value="{{user['username']}}"></dd>
    <dt>Password:</dt>
        <dd><input type="password" name="password1"></dd>
    <dt>Repeat password:</dt>
        <dd><input type="password" name="password2"></dd>
    <dt>Имя:</dt>
        <dd><input type="text" name="first_name" value="{{user['first_name']}}"></dd>

    <dt>Фамилия:</dt>
        <dd><input type="text" name="last_name" value="{{user['last_name']}}"></dd>

    <dt>Отчество:</dt>
        <dd><input type="text" name="middle_name" value="{{user['middle_name']}}"></dd>

    <dt>Группа:</dt>
        <dd><input type="text" name="study_group" value="{{user['study_group']}}"></dd>

    <dt>Почта:</dt>
        <dd><input type="text" name="email" value="{{user['email']}}"></dd>

    <dt>Телефон:</dt>
        <dd><input type="text" name="phone_number" value="{{user['phone_number']}}"></dd>

    <dt>Skype:</dt>
        <dd><input type="text" name="skype" value="{{user['skype']}}"></dd>
    
    <dt>ICQ:</dt>
        <dd><input type="text" name="icq" value="{{user['icq']}}"></dd>
</dl>
<input type="submit" value="Save">
</form>


</body>

</html>