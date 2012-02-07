all:
	python blog.py
config:
	exec `export BLOG_SETTINGS=config.py` && python config.py
test:
	mv blog.db blog.db.bak && python unittests.py && mv blog.db.bak blog.db
clean:
	rm blog.db blog.pyc
