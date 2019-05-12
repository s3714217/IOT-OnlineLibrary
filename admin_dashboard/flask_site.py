from datetime import datetime
from urllib import request
import json
import requests
from flask import render_template, request, redirect, url_for, flash, Blueprint
from wtforms import StringField, PasswordField, Form
from wtforms.validators import DataRequired

"""
Routes and views for the flask application.
"""

site = Blueprint("site", __name__)
logged_in = False
username = ''


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


@site.route('/')
@site.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )


@site.route('/login', methods=['GET', 'POST'])
def login():
    """Renders the login page."""
    form = LoginForm(request.form)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'jaqen' and password == 'hghar':
            logged_in = True
            username = username
            return redirect(url_for('site.dashboard'))
        else:
            flash("Error: Invalid login credentials")

    return render_template(
        'login.html',
        title='Login',
        form=form,
        year=datetime.now().year,
        message='Login to admin dashboard'
    )


@site.route('/logout')
def logout():
    logged_in = False
    username = ''
    return redirect(url_for('site.home'))


@site.route('/dashboard')
def dashboard():
    """Renders the dashboard page."""
    response = requests.get("http://127.0.0.1:5000/books")
    print(response)
    books = json.loads(response.text)

    return render_template(
        'dashboard.html',
        title='Dashboard',
        year=datetime.now().year,
        message='Manage the library',
        books=books
    )
