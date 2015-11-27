MYAPP
=====

SOME_DESCRIPTION


Development environment
-----------------------

To setup development environment::

   virtualenv .
   . bin/activate
   pip install -U setuptools pip pip-tools
   make


Bootswatch theme
================

Default bootswatch theme is 'cosmo'.

To change theme, change 'booswatch' variable in top-level Makefile.

To try other theme, just::

   make clean;
   make bootswatch=<THEME>
