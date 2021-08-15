from flask import Flask, session, request, redirect, url_for
from flask.templating import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, RadioField


class SignUp(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')


class Radio_ON(FlaskForm):
    select = RadioField(label='Select', choices=[("ON", "ON"), ("OFF", "OFF")])
    submit = SubmitField('Submit')


class Radio_SEC(FlaskForm):
    select = RadioField(label='Select mode', choices=[("Man", "Manual"), ("Sch", "Schedule"), ("Auto", "Automatic")])
    submit = SubmitField('Submit')


class Radio_EDIT(FlaskForm):
    select = RadioField(label='Edit mode', choices=[("Man", "Edit Manual"), ("Sch", "Edit Schedule"), ("Auto", "Edit Automatic")])
    submit = SubmitField('EDIT')


class Button_Edit(FlaskForm):
    select = SelectField(label='Select', choices=[("mode", "Edit mode"), ("edit","Edit stuff in modes")])
    submit = SubmitField('Submit')


class Button_Change_Mode(FlaskForm):
    submit = SubmitField('Change Mode')


class What_Edit(FlaskForm):
    select = SelectField(label='Select', choices=[("man", "Manual"), ("sch", "Schedule"), ("auto", "Automatic")])
    submit = SubmitField('Submit')

class What_Zone(FlaskForm):
    select = SelectField(label='Select', choices=[("1", "Zone 1"), ("2", "Zone 2"), ("3", "Zone 3"), ("4", "Zone 4")])
    submit = SubmitField('Submit')