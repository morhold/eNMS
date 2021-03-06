from flask_wtf import FlaskForm
from wtforms import (
    FloatField,
    IntegerField,
    TextField,
    PasswordField,
    SelectField,
    SelectMultipleField
)

## login and registration


class LoginForm(FlaskForm):
    name = TextField('Username')
    password = PasswordField('Password')


class CreateAccountForm(FlaskForm):
    name = TextField('Username')
    email = TextField('Email')
    password = PasswordField('Password')

## users management


class AddUser(FlaskForm):
    name = TextField('Username')
    email = TextField('Email')
    access_right_choices = (('Read-only',) * 2, ('Read-write',) * 2)
    access_rights = SelectField('Access rights', choices=access_right_choices)
    password = PasswordField('Password')


class DeleteUser(FlaskForm):
    users = SelectMultipleField('Users', choices=())

## administration


class TacacsServerForm(FlaskForm):
    ip_address = TextField('IP address')
    password = PasswordField('Password')
    port = IntegerField('Port', default=49)
    timeout = IntegerField('Timeout', default=10)


class SyslogServerForm(FlaskForm):
    ip_address = TextField('IP address', default='0.0.0.0')
    port = IntegerField('Port', default=514)

## parameters


class GeographicalParametersForm(FlaskForm):
    default_longitude = FloatField('Default longitude')
    default_latitude = FloatField('Default latitude')
    default_zoom_level = IntegerField('Default zoom level')
