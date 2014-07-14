<!DOCTYPE html>
<html>
<head>
  <title></title>
</head>
<body>
<form action="edit_profile_post" method="post">
    Firstname: <input type="text" name="firstname" value="{{firstname}}"><br>
    Lastname: <input type="text" name="lastname" value="{{lastname}}"><br>
    Study group: <input type="text" name="study_group" value="{{study_group}}"><br>
    <input type="hidden" name="username" value="{{username}}">
    <input type="submit" value="Send">
</form>
</body>
</html>
