# -*- coding: utf-8 -*-

import re
import os
from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config
from datetime import datetime

# Creates a Flask app and reads the settings from a
# configuration file. We then connect to the database specified
# in the settings file
app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


######################### Database Models #########################

class Comments(db.Model):
    """Setting the table name and
    creating columns for various fields"""
    __tablename__ = 'comments'
    id = db.Column('comment_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    comment = db.Column(db.String(200))
    pub_date = db.Column(db.DateTime)

    def __init__(self, name, email, comment):
        """Initializes the fields with entered data
        and sets the published date to the current time"""
        self.name = name
        self.email = email
        self.comment = comment
        self.pub_date = datetime.now()

class User(db.Model):

    __tablename__ = 'user'
    # id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


################### Flask Routes ################################

@app.route('/show')
def show_all():
    """The default route for the app. Displays the list of
    already entered the comments"""
    return render_template('show_all.html',
       comments=Comments.query.order_by(Comments.pub_date.desc()).all())

@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        # The request is POST with some data, get POST data and validate it.
        # The form data is available in request.form dictionary.
        # Check if all the fields are entered. If not, raise an error
        if not request.form['name'] or not request.form['email'] or not request.form['comment']:
            flash('Please enter all the fields', 'error')
        else:
            # The data is valid. So create a new 'Comments' object
            # to save to the database
            comment = Comments(request.form['name'],
                               request.form['email'],
                               request.form['comment'])

            # Add it to the SQLAlchemy session and commit it to
            # save it to the database
            db.session.add(comment)
            db.session.commit()

            # Flash a success message
            flash('Comment was successfully submitted')

            # Redirect to the view showing all the comments
            return redirect(url_for('show_all'))

    # Render the form template if the request is a GET request or
    # the form validation failed
    return render_template('new.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':
        if not request.form['username']:
            flash('Please enter username', 'error')
        elif not request.form['email']:
            flash('Please enter email', 'error')
        elif not request.form['password']:
            flash('Please enter password', 'error')
        else:
            user = User(request.form['username'],
                        request.form['email'],
                        request.form['password'])
        db.session.add(user)
        db.session.commit()

        flash('User is successfully created')

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route("/")
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        if not request.form['username']:
            flash('Please enter username', 'error')
        elif not request.form['password']:
            flash('Please enter password', 'password')
        else:
            result = db.session.query(User).filter(User.username==request.form['username'],
                User.password==request.form['password']).one()

            if result is not None:
                flash('You have login successfully! Welcome {username}'.format(username=request.form['username']))
                return redirect(url_for('show_all'))

    return render_template('login.html')


# This is the code that gets executed when the current python file is
# executed.
if __name__ == '__main__':
    # Run the app on all available interfaces on port 80 which is the
    # standard port for HTTP
    db.create_all()

    port = int(os.environ.get("PORT", 33507))
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
