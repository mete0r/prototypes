THEME_DIR := MYAPP/static/theme
DEFORM_DIR:= MYAPP/static/deform

all: theme deform

theme:
	make -C $(THEME_DIR)

deform:
	make -C $(DEFORM_DIR)

clean:
	make -C $(THEME_DIR) clean
	make -C $(DEFORM_DIR) clean
