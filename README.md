# Fate Aspect manager

Click on an aspect after you used it against a player. Cards and aspects will be re-sorted so that player aspects can be triggered in a fair distribution.

## Quality and Background

I just did the GTK tutorial and wanted to find a challenge to test my new learned skills (and experiment with GTK). For this reason this code is currently:

* Totally hacky (i tested stuff)
* Not best practice (same reason)

By sheer accident it is not totally useless. So I will be leaving it here and clean up the code (with GTK best practice).


## TIL

I wrote this to learn some GTK + Python. Learned from writing my first GTK application

### Worth doing

* Create Application object right from start
* Export UI into glade XML file

### Gettext

https://docs.python.org/3/library/gettext.html

https://stackoverflow.com/questions/10094335/how-to-bind-a-text-domain-to-a-local-folder-for-gettext-under-gtk3#10540744

Use pybabel to extract strings from python files, xgettext to add strings from glade files on top

Workflow:
* Extract strings (pybabel + xgettext)
* init new localisation files (msginit)
* translate manually
* generate .mo binary files (msgfmt)
