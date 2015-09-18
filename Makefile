node_modules_bin ?= $(abspath $(dir $(lastword $(MAKEFILE_LIST))))/node_modules/.bin/

lessc := $(node_modules_bin)lessc
lessc_options += $(if $(LESS_INCLUDE_PATH), --include-path=$(LESS_INCLUDE_PATH))
minify := $(node_modules_bin)minify
bower := $(node_modules_bin)bower
npmtools := $(lessc) $(minify) $(bower)

THEME_DIR := MYAPP/static/theme
DEFORM_DIR:= MYAPP/static/deform

all: theme deform

$(npmtools):
	npm install less minify bower --save-dev

theme: $(npmtools)
	make -C $(THEME_DIR) node_modules_bin=$(node_modules_bin)

deform: $(npmtools)
	make -C $(DEFORM_DIR) node_modules_bin=$(node_modules_bin)

clean:
	make -C $(THEME_DIR) clean
	make -C $(DEFORM_DIR) clean
