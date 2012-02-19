all:
	python2 blog.py
config:
	exec `export BLOG_SETTINGS=config.py` && python2 config.py
test:
	mv blog.db blog.db.bak && python2 unittests.py && mv blog.db.bak blog.db
clean:
	rm blog.db blog.pyc
