include Makefile.rules

BOOTSTRAP_FONTS_PATH := ../../bower_components/bootstrap/fonts

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

all: $(TARGETS)

$(CSS_FILES): LESS_INCLUDE_PATH=less
css/bootstrap.css: less/bootswatch.less less/variables.less
$(FONTS): fonts/%: $(BOOTSTRAP_FONTS_PATH)/%
	[ -e fonts ] || mkdir fonts
	cp $(source) $(target)
