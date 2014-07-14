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
</body>

</html>