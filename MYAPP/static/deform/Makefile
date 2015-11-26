node_modules_bin ?= $(abspath $(dir $(lastword $(MAKEFILE_LIST))))/node_modules/.bin/
bower := $(node_modules_bin)bower
bower_components = ../../bower_components
modernizr := $(bower_components)/modernizr
modernizr_js := $(modernizr)/modernizr.js

all: $(modernizr_js)

$(modernizr): bower.json
	$(bower) install

$(modernizr_js): $(modernizr)
	cd $(modernizr) && npm install --production
	$(modernizr)/bin/modernizr -c $(modernizr)/lib/config-all.json -d $@
