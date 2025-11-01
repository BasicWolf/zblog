build:
	$(MAKE) -C src/blog build

devserver:
	$(MAKE) -C src/blog devserver

install:
	pip install -r requirements.txt

publish-from-ci:
	$(MAKE) -C src/blog publish-from-ci

clean:
	$(MAKE) -C src/blog clean



test:
	pytest src/pelican-plugins/simple_comments
