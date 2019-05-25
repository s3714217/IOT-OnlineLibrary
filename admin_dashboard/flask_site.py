from datetime import datetime
from urllib import request
import json
import requests
from flask import render_template, request, flash, Blueprint, session, redirect, url_for
from wtforms import StringField, PasswordField, Form, DateField
from wtforms.validators import DataRequired

"""
Routes and views for the flask application.
"""

site = Blueprint("site", __name__)


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class BookForm(Form):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    isbn = StringField('ISBN', validators=[DataRequired()])
    publishedDate = DateField('Published Date', validators=[DataRequired()])


@site.route('/')
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
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('site.dashboard'))
    form = LoginForm(request.form)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'jaqen' and password == 'hghar':
            session['logged_in'] = True
            session['username'] = username
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


@site.route('/addbook', methods=['GET', 'POST'])
def add_book():
    """Adds a book to the database"""
    form = BookForm(request.form)
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        published_date = request.form['publishedDate']
        book = {"title": title, "author": author, "isbn": isbn, "publishedDate": published_date}
        print(book)
        if form.validate():
            try:
                requests.post('http://127.0.0.1:5000/books', json=book)
            except Exception as e:
                flash("Error: " + str(e))
                return
            return redirect(url_for('site.dashboard'))
        else:
            flash("Error: Invalid book data")

    return render_template(
        'addBook.html',
        title='Add book',
        form=form,
        year=datetime.now().year,
        message='Add a book to the library'
    )


@site.route('/logout')
def logout():
    session['logged_in'] = False
    session['username'] = ''
    return home()


@site.route('/home')
@site.route('/dashboard')
def dashboard():
    """Renders the dashboard page."""
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('site.home'))
    response = requests.get("http://127.0.0.1:5000/books")
    books = json.loads(response.text)
    return render_template(
        'dashboard.html',
        title='Dashboard',
        year=datetime.now().year,
        message='Manage the library',
        books=books
    )


@site.route('/statistics')
def view_statistics():
    """Renders the book lending statistics by week-wise and day-wise"""
    return render_template(
        'statistics.html',
        title='Statistics',
        year=datetime.now().year
    )
