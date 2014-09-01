<!doctype html>
<html>
<head></head>
<body>
{{err}}
<form action="register" method='post'>
    <dl>
        <dt> Username:
        <dd><input name='username' type='text'> <br>
        <dt> Password:
        <dd><input name='password1' type='password'> <br>
        <dt> Confirm password:
        <dd><input name='password2' type='password'><br>
        <dt> Email:
        <dd><input name='email' type='text'><br>
        <dd><input type='hidden' name='post_hash' value=$hash/>
    </dl>
    <p>
    <dd><input type='submit' value='Enter'>
</form>



<form method="post" action="/user/save">
<dl>
    <dt>Login:</dt>
        <dd><input type="text" name="username" value="{{user['username']}}"></dd>
    <dt>Password:</dt>
        <dd><input type="password" name="pass1"></dd>
    <dt>Repeat password:</dt>
        <dd><input type="password" name="pass22"></dd>
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

    <input type="hidden" name="uid" value="{{uid}}">
</dl>
<input type="submit" value="Save">
</form>


</body>

</html>