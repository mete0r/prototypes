include Makefile.rules

BOWER_COMPONENTS := ../../bower_components
BOOTSTRAP_FONTS_PATH := $(BOWER_COMPONENTS)/bootstrap/fonts

# Sources

BOOTSTRAP_FONTS := $(wildcard $(BOOTSTRAP_FONTS_PATH)/*)
LESS_FILES	:= less/bootstrap.less

# Targets

FONTS	:= $(addprefix fonts/, $(notdir $(BOOTSTRAP_FONTS)))
TARGETS	+= $(FONTS)

# Rules

debug:
	@echo FONTS: $(FONTS)
	@echo LESS_FILES: $(LESS_FILES)
	@echo CSS_FILES: $(CSS_FILES)
	@echo TARGETS: $(TARGETS)

all: $(BOWER_COMPONENTS) $(TARGETS)

$(CSS_FILES): LESS_INCLUDE_PATH=less
css/bootstrap.css: less/bootswatch.less less/variables.less
$(FONTS): fonts/%: $(BOOTSTRAP_FONTS_PATH)/%
	[ -e fonts ] || mkdir fonts
	cp $(source) $(target)
$(BOWER_COMPONENTS): $(bower)
	$(bower) install
