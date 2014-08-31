<!DOCTYPE html>
<html>

<head>
</head>

<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>

<style type="text/css" media="screen, (max-width: 640px)">
	html, body
	{
		font-family: Verdana, Tahoma, Arial;
		font-size: 32pt;
		height: 100%;
		margin: 0px;
		overflow: hidden;
		padding: 0px;
		width: 100%;
	}
	html { display: table; }
	body { display: table-cell; vertical-align: middle; }

	input, div.checkbox
	{
		background: #EEE;
		border: 1px solid #CCC;
		border-radius: 8px;
		font-family: Verdana, Tahoma, "Courier New", mono;
		font-size: 24pt;
		margin: 0px 0px 2px;
		overflow: auto;
		padding: 0px 2px;
		text-decoration: none;
	}
	input.down, div.checkbox { border-bottom-color: #EEE; border-right-color: #EEE; }
	input.up { border-top-color: #EEE; border-left-color: #EEE; }
	div.checkbox
	{
		display: inline-block;
		height: 24pt;
		vertical-align: text-bottom;
		width: 24pt;
	}
	div.checkbox.checked
	{
		background-image: url('checked-2.gif');
		background-repeat: no-repeat;
		background-position: center;
	}

	div.login-form div.msg { display: none; text-align: center; }
	div.login-form
	{
		margin: 0 auto;
		text-align: justify;
		width: 14em;
	}
	div.login-form dl { margin: 0px; }
	div.login-form dl dt
	{
		float: left;
		text-align: right;
		width: 6em;
	}
	div.login-form dl dd { margin-left: 6em; padding-left: 6px; }
	div.login-form dl input[type="checkbox"] { display: none; }
	div.login-form dl input { width: 10em; }

	div.login-form div.buttons { margin-top: 8px; text-align: center; }
	div.buttons a, div.buttons button
	{
		border: none;
		border-radius: 8px;
		display: inline-block;
		padding: 2px;
	}
	div.login-form div.buttons button { vertical-align: -8px; }
	div.login-form div.buttons img { vertical-align: text-bottom; }
	div.login-form div.buttons img { width: 64px; }
	div.login-form div.buttons a.g { background: #D34724; }
	div.login-form div.buttons a.f { background: #3C599B; }
	div.login-form div.buttons a.vk { background: #4C75A3; }
</style>

<body>
	{{err}}
	<a href="register">Register</a>
	<form action="passlogin" method="POST">
		<div class="login-form">
			<div class="msg">{{err}}</div>
			<dl>
				<dt>Login:</dt>
				<dd><input name="username" type="text" tabindex="1" maxlength="20" class="down" ></dd>
				<dt>Password:</dt>
				<dd><input name="password" type="password" tabindex="2" maxlength="20" class="down" ></dd>
				<dt></dt>
				<dd><label><div class="checkbox" id="remember"></div><input name="remember" type="checkbox" tabindex="5" value="1" onchange="$('#remember').toggleClass('checked');"> remember</label></dd>
			</dl>
			<div class="buttons">
				<a href="{{gurl}}" class="g"><img src="g.gif" title="login with google.com" alt="login with google.com" ></a>
				<a href="{{fburl}}" class="f"><img src="f.gif" title="login with facebook.com" alt="login with facebook.com" ></a>
				<a href="{{vkurl}}" class="vk"><img src="vk.gif" title="login with vk.com" alt="login with vk.com" ></a>
				<button type="submit"><img src="login.gif" title="login" alt="login" ></button>
			</div>
		</div>
	</form>

</body>

</html>