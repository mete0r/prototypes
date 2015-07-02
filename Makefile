THEME_DIR := MYAPP/static/theme

theme:
	make -C $(THEME_DIR)

clean:
	make -C $(THEME_DIR) clean
