# -*- coding: utf-8 -*-
"""
Unit tests for blog.py
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
        self.user = ['user', 'password']
        test_user = blog.User(self.user[0], self.user[1])
        blog.db.session.add(test_user)
        blog.db.session.commit()

    def tearDown(self):
        """Get rid of the database again after each test."""
        blog.db.drop_all()
        os.unlink(blog.app.config['DATABASE'])

    def login(self, user):
        return self.app.post('/login', data=dict(
            username=user[0],
            password=user[1]
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def make_post(self, post):
        self.login(self.user)
        rv = self.app.post('/add', data=post, follow_redirects=True)
        return rv

    # testing functions

    def test_empty_db(self):
        """Start with a blank database."""
        rv = self.app.get('/')
        assert 'No posts here so far' in rv.data

    def test_login_logout(self):
        """Make sure login and logout works"""
        rv = self.login(self.user)
        assert 'You were logged in' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data
        rv = self.login(['baduser', 'password'])
        assert 'Invalid username or password' in rv.data
        rv = self.login(['user', 'badword'])
        assert 'Invalid username or password' in rv.data

    def test_posts(self):
        """Test that posting works"""
        post = dict(title='<Hello>', text='<strong>HTML</strong> allowed here')
        rv = self.make_post(post)
        assert 'No entries here so far' not in rv.data
        assert '&lt;Hello&gt;' in rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data

    def test_pagination(self):
        """Test that pagination works"""
        result_when_PER_PAGE_exceeded = """Page:
            
              
                <strong>1</strong>
              
            
            
              
                <a href="/posts/page/2">2</a>
              
            
          
              <a href="/posts/page/2">Next &raquo;</a>"""
        posts = []
        for i in range(blog.PER_PAGE):
            post = dict(title='title ' + str(i), text='text ' + str(i))
            rv = self.make_post(post)
            assert result_when_PER_PAGE_exceeded not in rv.data
        rv = self.make_post(dict(title='I exceed PER_PAGE', text='pagination should occur now'))
        assert result_when_PER_PAGE_exceeded in rv.data


if __name__ == '__main__':
    unittest.main()
