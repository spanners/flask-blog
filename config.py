DEBUG = True
SQLALCHEMY_DATABASE_URI='sqlite:///blog.db'
SECRET_KEY = "development-key"

from blog import db, User

if DEBUG:
	db.create_all()
	admin = User('test', 'pass')
	db.session.add(admin)
	db.session.commit()
