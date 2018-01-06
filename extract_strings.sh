#!/bin/bash
#
# Create basic translation file

pybabel extract -k _ -o translation/en.pot fam.py
xgettext --keyword=translateable -j --sort-output -o translation/en.pot ui/fam.glade

msginit --locale=en --input=translation/en.pot
msginit --locale=de --input=translation/en.pot
