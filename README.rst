METE0R-PROJECT
==============

SOME_DESCRIPTION


Production environment
----------------------

To setup production environment::

   python bootstrap-virtualenv.py

Maintenance note: you should populate virtualenv_support/ with wheels for
production environment, i.e. packages specified in requirements.txt


Development environment
-----------------------

To setup development environment::

   virtualenv -p python3 .
   bin/pip install -U setuptools pip pip-tools
   make
   make test
