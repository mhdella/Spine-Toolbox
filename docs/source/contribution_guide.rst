..  Contribution guide
    Created: 19.6.2018

.. _Qt Style Sheets: http://doc.qt.io/qt-5/stylesheet.html
.. _PEP-8: https://www.python.org/dev/peps/pep-0008/

************************************
Contribution Guide for Spine Toolbox
************************************
All are welcome to contribute!

Coding Style
============
Follow the style you see used in the repository! Consistency with the rest of the project always
trumps other considerations. It doesn't matter if you have your own style or if the rest of the code
breaks with the greater community - just follow along.

Spine Toolbox coding style follows PEP-8_ style guide for Python code with the following variations:

* Maximum line length is 120 characters. Longer lines are acceptable if there's a sound reason.
* Google style docstrings with the title and input parameters are required for all classes, functions, and methods.
  For small functions or methods only the summary is necessary. Return types are highly recommended but not required
  if it is obvious what the function or method returns.
* Other deviations from PEP-8 can be discussed if there are good reasons.

Contributing to the User Guide
==============================
Spine Toolbox uses Sphinx to create HTML pages from restructured text (.rst) files. The .rst files are
plain text files that are formatted in a way that Sphinx understands and is able to turn them into HTML.
You can find a brief introduction to reStructured text in (http://www.sphinx-doc.org/en/stable/rest.html).
You can modify the existing or create new .rst files into ``docs/source`` directory. When you are done editing, run
``bin/build_doc.bat`` on Windows or ``bin/build_doc.sh`` on Linux to build the HTML pages. The created pages are
found in ``docs/build/html`` directory. Both scripts first run the sphinx-apidoc tool, which reads DocStrings from
the source code and turns them into a nice looking API HTML reference automatically.

Contributing to the Spine Toolbox Graphical User Interface
==========================================================
If you want to change or add new widgets into the application, you need to use the ``bin/build_ui.bat`` (Windows) or
``bin/build_ui.sh`` (Linux) scripts. The main design of the widgets should be done with Qt Designer (``designer.exe``
or ``designer``) that is included with PySide2. The files produced by Qt Designer are XML files (.ui). You can
also embed graphics (e.g. icons, logos, etc.) into the application by using Qt Designer. When you are done
modifying widgets in the designer, you need to run the ``build_ui`` script for the changes to take effect.
This script uses tools provided in the PySide2 package to turn .ui files into Python files, in essence
rebuilding the whole Spine Toolbox user interface.

Styling the widgets should be done with `Qt Style Sheets`_ in code. Avoid using style sheets in Qt Designer.

Reporting Bugs
==============

This section is based on a set of best practices for open source projects (http://contribution-guide-org.readthedocs.io/)

Due Diligence
-------------
Before submitting a bug report, please do the following:

**Perform basic troubleshooting steps.**

1. **Make sure you’re on the latest version.** If you’re not on the most recent version,
   your problem may have been solved already! Upgrading is always the best first step.
2. **Try older versions.** If you’re already on the latest release, try rolling back a
   few minor versions (e.g. if on 1.7, try 1.5 or 1.6) and see if the problem goes away.
   This will help the devs narrow down when the problem first arose in the commit log.
3. **Try switching up dependency versions.** If you think the problem may be due to a
   problem with a dependency (other libraries, etc.). Try upgrading/downgrading those as well.
4. **Search the project’s bug/issue tracker to make sure it’s not a known issue.** If you
   don’t find a pre-existing issue, consider checking with the maintainers in case the problem
   is non-bug-related.

What to Put in Your Bug Report
------------------------------
**Make sure your report gets the attention it deserves**: bug reports with missing
information may be ignored or punted back to you, delaying a fix. The below constitutes a
bare minimum; more info is almost always better:

1. What version of the Python interpreter are you using? E.g. Python 2.7.3, Python 3.6?
2. What operating system are you on? Windows? (Vista, 7, 8, 8.1, 10). 32-bit or 64-bit? Mac OS X?
   (e.g. 10.7.4, 10.9.0) Linux (Which distro? Which version of that distro? 32 or 64 bits?) Again, more
   detail is better.
3. Which version or versions of the software are you using? If you have forked the project from Git,
   which branch and which commit? Otherwise, supply the application version number (Help->About menu).
   Also, ideally you followed the advice above and have ruled out (or verified that the problem exists in)
   a few different versions.
4. How can the developers recreate the bug? What were the steps used to invoke it. A screenshot demonstrating
   the bug is usually the most helpful thing you can report (if applicable) Relevant output from the
   Event Log or debug messages from the console of your run, should also be included.

Feature Requests
================
The developers of Spine Toolbox are happy to hear new ideas for features or improvements to existing functionality.
The format for requesting new features is free. Just fill out the required fields on the issue tracker and give a
description of the new feature. A picture accompanying the description is a good way to get your idea into development
faster. But before you make a new issue, check that there isn't a related idea already open in the issue tracker. If
you have an idea on how to improve an existing issue, just join the conversation.

Submitting features/bugfixes
============================
If you feel like you can fix a bug that's been bothering you or you want to add a new feature to the application but
the devs seem to be too busy with something else, please follow these instructions.

Version Control Branching
-------------------------
Always make a new branch for your work, no matter how small. This makes it easy for others to take just
that one set of changes from your repository, in case you have multiple unrelated changes floating around.

A corollary: don't submit unrelated changes in the same branch/pull request! The maintainer shouldn't have
to reject your awesome bugfix because the feature you put in with it needs more review.

Base your new branch off of the appropriate branch on the main repository:

**Bug fixes should be based on the branch named after the oldest supported release line the bug affects**

    E.g. if a feature was introduced in 1.1, the latest release line is 1.3, and a bug is found in that
    feature - make your branch based on 1.1. The maintainer will then forward-port it to 1.3 and master.
    Bug fixes requiring large changes to the code or which have a chance of being otherwise disruptive,
    may need to base off of master instead. This is a judgement call – ask the devs!

**New features should branch off of the 'master' branch**

    Note that depending on how long it takes for the dev team to merge your patch, the copy of master
    you worked off of may get out of date! If you find yourself 'bumping' a pull request that’s been
    sidelined for a while, make sure you rebase or merge to latest master to ensure a speedier resolution.

Test-driven development is your friend
--------------------------------------
Any bug fix that doesn’t include a test proving the existence of the bug being fixed, may be suspect.
Ditto for new features that can’t prove they actually work.

It is recommended to use test-first development as it really helps make features better designed
and identifies potential edge cases earlier instead of later. Writing tests before the implementation
is strongly encouraged.

Full example
------------
Here’s an example workflow for a project ``theproject`` hosted on Github, which is currently in version
1.3.x. Your username is ``yourname`` and you’re submitting a basic bugfix. (This workflow only changes
slightly if the project is hosted at Bitbucket, self-hosted, or etc.)

**Preparing your Fork**

1. Click ‘Fork’ on Github, creating e.g. ``yourname/theproject``
2. Clone your project: ``git clone git@github.com:yourname/theproject``
3. ``cd theproject``
4. Create a virtual environment and install requirements
5. Create a branch: ``git checkout -b foo-the-bars 1.3``

**Making your Changes**

1. Add changelog entry crediting yourself.
2. Write tests expecting the correct/fixed functionality; make sure they fail.
3. Hack, hack, hack.
4. Run tests again, making sure they pass.
5. Commit your changes: ``git commit -m "Foo the bars"``

**Creating Pull Requests**

1. Push your commit to get it back up to your fork: ``git push origin HEAD``
2. Visit Github, click handy ‘Pull request‘ button that it will make upon noticing your new branch.
3. In the description field, write down issue number (if submitting code fixing an existing issue)
   or describe the issue + your fix (if submitting a wholly new bugfix).
4. Hit ‘submit’! And please be patient - the maintainers will get to you when they can.
