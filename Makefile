define ALL
	update-requirements
	theme
	deform
endef
ALL:=$(shell echo $(ALL))  # to remove line-feeds

define REQUIREMENTS_FILES
	requirements-dev.txt
	requirements.txt
endef
REQUIREMENTS_FILES:=$(shell echo $(REQUIREMENTS_FILES))

define REQUIREMENTS_IN
	requirements-site.in
	requirements-app.in
endef
REQUIREMENTS_IN:=$(shell echo $(REQUIREMENTS_IN))

define REQUIREMENTS_IN_DEV
	requirements-dev.in
	requirements-test.in
	requirements-site.in
	requirements-app.in
endef
REQUIREMENTS_IN_DEV:=$(shell echo $(REQUIREMENTS_IN_DEV))

offline?=0


all: $(ALL)

.PHONY: update-requirements

ifeq (1,$(offline))
PIP_NO_INDEX:=--no-index
endif

FIND_LINKS:=-f wheelhouse

update-requirements: $(REQUIREMENTS_FILES)
	. bin/activate && bin/pip-sync $(FIND_LINKS) $(PIP_NO_INDEX) requirements-dev.txt

requirements.txt: $(REQUIREMENTS_IN)
	. bin/activate && bin/pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) -o $@ $^

requirements-dev.txt: $(REQUIREMENTS_IN_DEV)
	. bin/activate && bin/pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) -o $@ $^

.PHONY: update-wheelhouse
update-wheelhouse: requirements-dev.txt
	bin/pip wheel -r $< -w wheelhouse $(PIP_NO_INDEX)

THEME_DIR := MYAPP/static/theme
DEFORM_DIR:= MYAPP/static/deform

theme:
	make -C $(THEME_DIR)

deform:
	make -C $(DEFORM_DIR)

clean:
	make -C $(THEME_DIR) clean
	make -C $(DEFORM_DIR) clean
