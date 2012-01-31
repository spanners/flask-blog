# -*- coding: utf-8 -*-
"""
"""
import os
import flaskr
import tempfile
import unittest

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        """Before each test, set up a blank database"""
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        self.app = flaskr.app.test_client()
        flaskr.db.create_all()
        admin = flaskr.User('admin', 'poop')
        flaskr.db.session.add(admin)
        flaskr.db.session.commit()

    def tearDown(self):
        """Get rid of the database again after each test."""
        flaskr.db.drop_all()
        os.unlink(flaskr.app.config['DATABASE'])

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
        rv = self.login('admin', 'poop')
        assert 'You were logged in' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data
        rv = self.login('badmiin', 'poop')
        assert 'Invalid username or password' in rv.data
        rv = self.login('admin', 'pooop')
        assert 'Invalid username or password' in rv.data

    def test_messages(self):
        """Test that messages work"""
        self.login('admin', 'poop')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert '&lt;Hello&gt;' in rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data


if __name__ == '__main__':
    unittest.main()
