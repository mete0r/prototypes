node_modules_bin ?= $(abspath $(dir $(lastword $(MAKEFILE_LIST))))/node_modules/.bin/

lessc := $(node_modules_bin)lessc
lessc_options += $(if $(LESS_INCLUDE_PATH), --include-path=$(LESS_INCLUDE_PATH))
minify := $(node_modules_bin)minify
bower := $(node_modules_bin)bower
npmtools := $(lessc) $(minify) $(bower)

THEME_DIR := MYAPP/static/theme
DEFORM_DIR:= MYAPP/static/deform
DEFORM_SIGNATURE_DIR:= MYAPP/widgets/signature

all: theme deform deform.signature pot mo-files

$(npmtools):
	npm install less minify bower --save-dev

theme: $(npmtools)
	make -C $(THEME_DIR) node_modules_bin=$(node_modules_bin)

deform: $(npmtools)
	make -C $(DEFORM_DIR) node_modules_bin=$(node_modules_bin)

deform.signature: $(npmtools)
	make -C $(DEFORM_SIGNATURE_DIR) node_modules_bin=$(node_modules_bin)

LOCALE_PREFIX := MYAPP/locale/
POT_PACKAGE_NAME := MYAPP
POT_PACKAGE_VERSION := 0.0.0
POT_MSGID_BUGS_ADDRESS := mete0r@sarangbang.or.kr
POT_COPYRIGHT_HOLDER   := mete0r@sarangbang.or.kr
POT_DOMAIN := MYAPP
POT_FILE := $(LOCALE_PREFIX)$(POT_DOMAIN).pot
PO_LANGUAGES := ko
PO_SUFFIX := /LC_MESSAGES/$(POT_DOMAIN).po
MO_SUFFIX := /LC_MESSAGES/$(POT_DOMAIN).mo
PO_FILES = $(addprefix $(LOCALE_PREFIX),$(addsuffix $(PO_SUFFIX),$(PO_LANGUAGES)))
MO_FILES = $(addprefix $(LOCALE_PREFIX),$(addsuffix $(MO_SUFFIX),$(PO_LANGUAGES)))

.PHONY: pot
.PHONY: pot-clean
.PHONY: po-files
.PHONY: mo-files

pot: $(POT_FILE)
$(POT_FILE):
	bin/pot-create	--package-name $(POT_PACKAGE_NAME)\
			--package-version $(POT_PACKAGE_VERSION)\
			--msgid-bugs-address $(POT_MSGID_BUGS_ADDRESS)\
			--copyright-holder $(POT_COPYRIGHT_HOLDER)\
			-d $(POT_DOMAIN)\
			-o $@\
			MYAPP
pot-clean:
	rm -f $(POT_FILE)

po-files: $(PO_FILES)

$(PO_FILES): $(POT_FILE)
	mkdir -p $(dir $@)
	[ -e $@ ] || msginit -i $< -o $@ -l $(subst $(LOCALE_PREFIX),,$(subst $(PO_SUFFIX),,$@))
	[ -e $@ ] && msgmerge --update --lang=$(subst $(LOCALE_PREFIX),,$(subst $(PO_SUFFIX),,$@)) $@ $<

mo-files: $(MO_FILES)
%.mo: %.po
	msgfmt -o $@ $<


clean:
	make -C $(THEME_DIR) clean
	make -C $(DEFORM_DIR) clean
