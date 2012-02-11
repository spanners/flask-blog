# -*- coding: utf-8 -*-
"""
A blog!
"""

from flask import Flask
from flask import abort
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flaskext.sqlalchemy import SQLAlchemy
from datetime import datetime


APP = Flask(__name__)
APP.config.from_envvar('BLOG_SETTINGS', silent=True)
DB = SQLAlchemy(APP)


class Posts(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    title = DB.Column(DB.String(80))
    text = DB.Column(DB.Text)
    pub_date = DB.Column(DB.DateTime)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'))

    def __init__(self, user, title, text, pub_date=None):
        self.user = user
        self.title = title
        self.text = text
        self.pub_date = datetime.utcnow()

    def __repr__(self):
        return '<Posts %r>' % self.title

class User(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(80), unique=True)
    password = DB.Column(DB.String(120))
    posts = DB.relationship(Posts, lazy='dynamic', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username


@APP.template_filter('datetimeformat')
def datetimeformat(value, format='%H:%M on %d/%m/%Y'):
    return value.strftime(format)


@APP.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


PER_PAGE = 5

@APP.route('/')
@APP.route('/posts/', defaults={'page': 1})
@APP.route('/posts/page/<int:page>')
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

APP.jinja_env.globals['url_for_other_page'] = url_for_other_page


@APP.route('/add', methods=['POST'])
def add_post():
    if not session.get('logged_in'):
        abort(401)
    post = Posts(g.user, request.form['title'], request.form['text'])
    DB.session.add(post)
    DB.session.commit()
    flash('New post was successfully posted')
    return redirect(url_for('show_posts'))


@APP.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            DB.session.add(user)
            DB.session.commit()
            session['user_id'] = user.id
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_posts'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)


@APP.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_posts'))


if __name__ == '__main__':
    # create our little application :)
    if DEBUG:
        APP.run()
    else:
        APP.run(host='0.0.0.0')
