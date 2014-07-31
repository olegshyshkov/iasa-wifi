<!doctype html>
<html>
<head>
<link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>

    <div class="nav">
        <ul>
            <li><a href="register">Registation</a></li>
            <li><a href='change.php'>Change password</a><li>
        </ul>  
    </div>
    
    {{err}}

    <div align="center">
        <form action="login" method="post">
        <table>
            <tr><td>Login:</td> <td><input name="username" type="text" size="10"><br></td></tr>
            <tr><td>Password:</td> <td><input name="password" type="password" size="10"></td></tr>
        </table>
                <input type="submit" value="Enter">
        </form>
    </div>
</body>

