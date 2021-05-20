from wtforms import Form, IntegerField, PasswordField

# User Login Form with WTF Form
class LoginForm(Form):
    username = IntegerField("User ID")
    password = PasswordField("Password")
