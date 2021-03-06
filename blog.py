# -*- coding: utf-8 -*-
"""
A blog!
"""

import os
from flask import Flask
from flask import abort
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import send_from_directory
from flaskext.sqlalchemy import SQLAlchemy
from datetime import datetime


DEBUG = True
SQLALCHEMY_DATABASE_URI='sqlite:///blog.db'
SECRET_KEY = "development-key"


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('BLOG_SETTINGS', silent=True)
db = SQLAlchemy(app)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    text = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, user, title, text, pub_date=None):
        self.user = user
        self.title = title
        self.text = text
        self.pub_date = datetime.utcnow()

    def __repr__(self):
        return '<Posts %r>' % self.title

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship(Posts, lazy='dynamic', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username



@app.template_filter('datetimeformat')
def datetimeformat(value, format='%H:%M on %d/%m/%Y'):
    return value.strftime(format)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


PER_PAGE = 5

@app.route('/')
@app.route('/posts/', defaults={'page': 1})
@app.route('/posts/page/<int:page>')
def show_posts(page=1):
    posts = get_posts_for_page(page, PER_PAGE)
    pagination = Posts.query.filter_by(user=g.user).paginate(page, PER_PAGE)
    return render_template('show_entries.html',
        pagination=pagination,
        posts=posts
    )

def get_posts_for_page(page, per_page):
    all_posts = Posts.query.filter_by(user=g.user)
    start = (page * per_page) - per_page
    stop = start + per_page
    return all_posts.slice(start, stop)

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page


@app.route('/add', methods=['POST'])
def add_post():
    if not session.get('logged_in'):
        abort(401)
    post = Posts(g.user, request.form['title'], request.form['text'])
    db.session.add(post)
    db.session.commit()
    flash('New post was successfully posted')
    return redirect(url_for('show_posts'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_posts'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_posts'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
            'favicon.ico',
            mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    # create our little application :)
    if DEBUG:
        app.run()
    else:
        app.run(host='0.0.0.0')
