<!doctype html>
<html>
<head>
<link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>


<div class="nav">
    <ul>
        <li><a href="/administration">Administation</a></li>        
        <li><a href="user/edit_profile">Edit profile</a></li>
        <li><a href="/about">About</a></li>
        <li><a href="/logout">Logout</a></li>
    </ul>
</div>


<div>
    <h1>Hello {{ username }}!</h1>
</div>

<div class="container">
    <div class="social">
        <ul>
            <li><a href="{{fb_url}}">{{fb_name}}</a></li>
            <li><a href="{{g_url}}">{{g_name}}</a></li>
            <li><a href="{{vk_url}}">{{vk_name}}</a></li>
        </ul>
    </div>



    <div class="person">
        <ul>
            <li>Group: {{group}} </li>
            <li>Name: {{name}} </li>
            <li>Study group: {{study_group}}</li>
        </ul>
    </div>


    <div class="devices">
        <div class="curdev">
            <p>Your current device with mac: {{mac}} not registred in system. Link it with this account?</p>
            <ul>
                <li><a href="add_device?type=tablet">Tablet</a></li>
                <li>
                    <form action="add_device" method="post">
                        <input type="hidden" value="Tablet">
                        <input type="submit" value="Tablet">
                    </form>
                </li>
                <li><a href="add_device?type=mobile phone">Mobile phone</a></li>
                <li><a href="add_device?type=laptop">Laptop</a></li>
            </ul>
            </div>

        <div style="float:none;">
            <form action="add_device" method="post">
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
        </div>
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
</div>
%if group == 'admin':
Hello, Johny!
%end

</body>
</html>
