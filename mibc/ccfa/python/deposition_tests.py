#!/usr/bin/env python

"""
 script tests the respository for a given username and returns a simple
 'ok' for projects under the user the pass all the tests.  script returns
 errors for any tests in the projects that do not pass.
"""

from models import Repository, default_Repository, User, Project 
from validate import validate 
import tests
import sys, os
import argparse

# Argument parsing
argp = argparse.ArgumentParser( 
	prog = "deposition_tests.py", 
	description = """Runs deposition repository tests either from the web or from cli.""" )

argp.add_argument(
	"-u", 
	"--user", 
	dest = "user", 
	action = "store", 
	required = True, 
	help = "given user whose projects are tested")

largs = argp.parse_args()
if (largs.user is not None):

    repo = default_Repository()
    user = User(largs.user, repo, True)
    validate(user)
    for project in user.projects.all():
        print "<H3>Project %s Tests: </H3>" % project.name
        # print validate(project)
        print "<ul>"
        for check, msg in validate(project):
            if check == True:
                print "<li> Test Passed: %s </li>" % msg
            else:
                print "<li> Test Failed: %s </li>" % msg

        print "</ul>"

