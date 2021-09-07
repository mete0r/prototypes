define ALL
	update-requirements
endef
ALL:=$(shell echo $(ALL))  # to remove line-feeds

define REQUIREMENTS_FILES
	requirements/dev.txt
	requirements/docs.txt
	requirements/lint.txt
	requirements/test.txt
	requirements/site.txt
	requirements.txt
endef
REQUIREMENTS_FILES:=$(shell echo $(REQUIREMENTS_FILES))

define REQUIREMENTS_IN
	requirements.in
endef
REQUIREMENTS_IN:=$(shell echo $(REQUIREMENTS_IN))

define REQUIREMENTS_IN_SITE
	requirements.in
	requirements/site.in
endef
REQUIREMENTS_IN_SITE:=$(shell echo $(REQUIREMENTS_IN_SITE))

define REQUIREMENTS_IN_TEST
	requirements/setup.in
	requirements/test.in
	requirements.in
endef
REQUIREMENTS_IN_TEST:=$(shell echo $(REQUIREMENTS_IN_TEST))

define REQUIREMENTS_IN_LINT
	requirements/setup.in
	requirements/lint.in
endef
REQUIREMENTS_IN_LINT:=$(shell echo $(REQUIREMENTS_IN_LINT))

define REQUIREMENTS_IN_DOCS
	requirements/docs.in
	requirements.in
endef
REQUIREMENTS_IN_DOCS:=$(shell echo $(REQUIREMENTS_IN_DOCS))

define REQUIREMENTS_IN_DEV
	requirements/setup.in
	requirements/dev.in
	requirements/docs.in
	requirements/lint.in
	requirements/test.in
	requirements/site.in
	requirements.in
endef
REQUIREMENTS_IN_DEV:=$(shell echo $(REQUIREMENTS_IN_DEV))

offline?=0

ifeq (1,$(offline))
PIP_NO_INDEX:=--no-index
endif

FIND_LINKS:=-f virtualenv_support
VENV	:= . bin/activate &&


.PHONY: all
all: $(REQUIREMENTS_FILES) update-requirements

.PHONY: update-requirements
update-requirements: .pip-sync
.pip-sync: requirements/dev.txt
	$(VENV) pip-sync $(FIND_LINKS) $(PIP_NO_INDEX) $^
	$(VENV) pip freeze > $@.tmp && mv $@.tmp $@

requirements.txt: $(REQUIREMENTS_IN)
	$(VENV)	pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^
	$(VENV)	pip wheel $(FIND_LINKS) $(PIP_NO_INDEX) --no-deps -r $@ -w virtualenv_support

requirements/site.txt: $(REQUIREMENTS_IN_SITE)
	$(VENV) pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^
	$(VENV) pip wheel $(FIND_LINKS) $(PIP_NO_INDEX) --no-deps -r $@

requirements/test.txt: $(REQUIREMENTS_IN_TEST)
	$(VENV) pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^
	$(VENV) pip wheel $(FIND_LINKS) $(PIP_NO_INDEX) --no-deps -r $@

requirements/lint.txt: $(REQUIREMENTS_IN_LINT)
	$(VENV) pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^
	$(VENV) pip wheel $(FIND_LINKS) $(PIP_NO_INDEX) --no-deps -r $@

requirements/docs.txt: $(REQUIREMENTS_IN_DOCS)
	$(VENV) pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^
	$(VENV) pip wheel $(FIND_LINKS) $(PIP_NO_INDEX) --no-deps -r $@

requirements/dev.txt: $(REQUIREMENTS_IN_DEV)
	$(VENV) pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^
	$(VENV) pip wheel $(FIND_LINKS) $(PIP_NO_INDEX) --no-deps -r $@

.PHONY: bootstrap-virtualenv
bootstrap-virtualenv.py: requirements.txt bootstrap-virtualenv.in
	python setup.py virtualenv_bootstrap_script -o $@ -r $<


.PHONY: notebook
notebook:
	$(VENV)	jupyter notebook --notebook-dir=notebooks

.PHONY: test
test: requirements/test.txt
	$(VENV) coverage erase
	$(VENV) tox --parallel=4 -e lint,py39

.PHONY: test-report
test-report:
	$(VENV) coverage combine
	$(VENV) coverage report
	$(VENV) coverage html
	$(VENV) coverage xml

.PHONY: lint
lint:
	$(VENV) tox -e lint

.PHONY: docs
docs:
	$(VENV) tox -e docs

.PHONY: black
black:
	$(VENV) black --line-length=79 setup.py src tests docs/conf.py

# https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/i18n.html#extracting-messages-from-code-and-templates
.PHONY: msg-pot
msg-pot:
	$(VENV) pot-create\
		--output src/METE0R_PACKAGE/locale/METE0R-PROJECT.pot\
		--width 79\
		--sort-by-file\
		--copyright-holder "Yoosung Moon <yoosungmoon@naver.com>"\
		--package-name "METE0R-PROJECT"\
		--package-version "0.0.0"\
		--msgid-bugs-address yoosungmoon@naver.com\
		src

# https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/i18n.html#updating-a-catalog-file
.PHONY: msg-update
msg-update:
	msgmerge --update --backup=off --width=79 src/METE0R_PACKAGE/locale/en/LC_MESSAGES/METE0R-PROJECT.po src/METE0R_PACKAGE/locale/METE0R-PROJECT.pot
	msgmerge --update --backup=off --width=79 src/METE0R_PACKAGE/locale/ko/LC_MESSAGES/METE0R-PROJECT.po src/METE0R_PACKAGE/locale/METE0R-PROJECT.pot

.PHONY: run
run:
	$(VENV) pserve development.ini --reload

.PHONY: shell
shell:
	$(VENV) pshell development.ini
