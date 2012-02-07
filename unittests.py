# -*- coding: utf-8 -*-
"""
"""
import os
import blog
import tempfile
import unittest

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        """Before each test, set up a blank database"""
        self.db_fd, blog.app.config['DATABASE'] = tempfile.mkstemp()
        blog.app.config['TESTING'] = True
        self.app = blog.app.test_client()
        blog.db.create_all()
        test_user = blog.User('user', 'password')
        blog.db.session.add(test_user)
        blog.db.session.commit()

    def tearDown(self):
        """Get rid of the database again after each test."""
        blog.db.drop_all()
        os.unlink(blog.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    # testing functions

    def test_empty_db(self):
        """Start with a blank database."""
        rv = self.app.get('/')
        assert 'No posts here so far' in rv.data

    def test_login_logout(self):
        """Make sure login and logout works"""
        rv = self.login('user', 'password')
        assert 'You were logged in' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data
        rv = self.login('baduser', 'password')
        assert 'Invalid username or password' in rv.data
        rv = self.login('user', 'badword')
        assert 'Invalid username or password' in rv.data

    def test_messages(self):
        """Test that messages work"""
        self.login('user', 'password')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert '&lt;Hello&gt;' in rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data


if __name__ == '__main__':
    unittest.main()
