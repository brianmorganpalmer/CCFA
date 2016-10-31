
import os
import re
import datetime
import mimetypes
from types import *
from itertools import chain

import dateutil.parser

from models import (
    Repository,
    Project,
    User,
)
import efo
import settings


user_to_test    = "example_user"
project_to_test = "example_proj"


class ValidatorBase(object):

    def __init__(self, base=None, cheat_all_tests=False):
        self.cheat_all_tests = cheat_all_tests
        self.base = base
        self.conditions = list()

    def cond(self, cond, mesg):
        if cond is True:
            self.conditions.append((True, ""))
        else:
            self.conditions.append((cond, mesg))

    def all_tests_passed(self):
        if self.cheat_all_tests:
            return True
        else:
            ret = all([cond[0] for cond in self.conditions])
            self.conditions = list()
            return ret

    def __iter__(self):
        for key in dir(self):
            if key.startswith('test_'):
                yield getattr(self, key)



class Repository_Test(ValidatorBase):
    
    def setUp(self):
        if self.base:
            self.repo = base
        else:
            self.repo = Repository()

    def tearDown(self):
        del(self.repo)

    def test_instantiation(self):
        new_repo = Repository()

    def test_necessaryProperties(self):
        self.cond( type(self.repo.path) is StringType,
                   "Repository has no path"
        )
        self.cond( os.path.isdir(self.repo.path),
                   "The Repository path %s does not exist" %(self.repo.path)
        )
        assert self.all_tests_passed()

    def test_userList(self):
        allusers = self.repo.users.all()
        self.cond( type(allusers) is ListType,
                   "Unable to list users in repository"
        )
        self.cond( len(allusers) > 0,
                   "No users, even the example user, are found"
        )
        assert self.all_tests_passed()

    def test_userGet(self):
        user = self.repo.users[user_to_test]
        self.cond( len(user.name) > 0,
                   "Failed to test user %s"%(user.name)
        )
        assert self.all_tests_passed()


class User_Test(ValidatorBase):
    
    def setUp(self):
        if self.base:
            self.repo = self.base.repo
            self.user = self.base
        else:
            self.repo = Repository()
            self.user = self.repo.users[user_to_test]

    def tearDown(self):
        del(self.user)
        del(self.repo)

    def test_necessaryProperties(self):
        self.cond( type(self.user.path) is StringType,
                   "The user %s has a path that isn't a string"%(self.user.name)
        )
        self.cond( self.user.path == os.path.join( self.repo.path,
                                                   self.user.name ),
                   str("The path attribute for user %s "
                       "does not match the user's name")%(self.user.name)
        )
        assert self.all_tests_passed()

    def test_projectList(self):
        allprojects = self.user.projects.all()
        self.cond( type(allprojects) is ListType,
                   "Unable to list all projects under user %s"%(self.user.name)
        )
        self.cond( len(allprojects) > 0,
                   "User %s has no projects" %(self.user.name)
        )
        assert self.all_tests_passed()

    def test_projectGet(self):
        proj = self.user.projects[project_to_test]
        self.cond( len(proj.name) > 0,
                   "Failed to retrieve the project %s from user %s" %(
                       project_to_test, self.user.name)
        )
        assert self.all_tests_passed()


class Project_Test(ValidatorBase):

    required_fields = [
        "pi_first_name",
        "pi_last_name",
        "pi_contact_email",
        "lab_name",
        "researcher_first_name",
        "researcher_last_name",
        "researcher_contact_email",
        "study_title",
        "study_description",
        "filename",
        "collection_start_date",
        "collection_end_date"
        ]

    def setUp(self):
        if self.base:
            self.repo = self.base.user.repo
            self.user = self.base.user
            self.project = self.base
        else:
            self.repo = Repository()
            self.user = self.repo.users[user_to_test]
            self.project = self.user.projects[project_to_test]

    def tearDown(self):
        del( self.repo, self.user, self.project )


    def test_necessaryProperties(self):
        for field in self.required_fields:
            self.cond( getattr(self.project, field, None) is not None,
                       "Project %s is missing required field %s" %(
                           self.project.name, field )
            )

        assert self.all_tests_passed()


    def test_parseableDates(self):
        for field in [ self.project.collection_end_date,
                       self.project.collection_start_date ]:
            try:
                date = dateutil.parser.parse(field[0])
            finally:
                self.cond( type(date) is type(datetime.datetime(2013,12,05)),
                           "Project %s has an unreadable date %s"%(
                               self.project.name, field[0])
                )

        assert self.all_tests_passed()


    def test_emptyDates(self):
        self.cond( any(self.project.collection_start_date),
                   "Project %s has an emtpy collection_start_date"%(
                       self.project.name) )
        self.cond( any(self.project.collection_end_date),
                   "Project %s has an emtpy collection_end_date"%(
                       self.project.name) )

        assert self.all_tests_passed()


    def test_realisticDates(self):
        beg = dateutil.parser.parse(
            self.project.collection_start_date[0]
            )
        end = dateutil.parser.parse(
            self.project.collection_end_date[0]
            )
        self.cond( beg <= end,
                   str("Project %s has a end collection date "
                       "before its start collection date" )%(self.project.name)
        )
        assert self.all_tests_passed()        

    def test_filenamesExist(self):
        for basename in self.project.filename:
            fullpath = os.path.join( self.project.path,
                                     basename )
            self.cond( os.path.isfile(fullpath),
                       "Project %s: File specified %s does not exist" %(
                           self.project.name, fullpath)
            )

        assert self.all_tests_passed()


    def test_emailableContacts(self):
        for address in self.project.pi_contact_email + \
                       self.project.researcher_contact_email: 

            x = re.match(
                r'[a-zA-Z0-9._-]+@[0-9a-zA-Z._-]+\.[0-9a-zA-Z]+', 
                address
                )
            self.cond(x is not None,
                      "Project %s: Email address %s is not readable" %(
                          self.project.name, address)
            )
            
        assert self.all_tests_passed()

    def test_efo_metadata(self):
        to_validate = list()
        for line in chain(self.project.map[0]._fields,
                          self.project.map):
            guesses = efo.guess(*line)
            to_validate.extend(
                [ efo_id for efo_id, guess in guesses.iteritems()
                  if guess is True ]
            )

        for efo_id, valid in efo.parallel_validate(*to_validate).iteritems():
            self.cond( valid is True,
                       "Guessed EFO %s is not valid" %(efo_id)
                   )

        assert self.all_tests_passed()

    def test_no_tars(self):
        for filename in self.project.filename:
            self.cond( 
                "application/x-tar" not in mimetypes.guess_type(filename),
                "Uploaded tarfiles are not supported"
            )

        assert self.all_tests_passed()


    def test_16S_things(self):
        if getattr(self.project, "16s_data", [False])[0] == "true":
            self.cond( self.project.exists() is True,
                       "The project does not exist" )
            self.cond( len(self.project.map) > 0,
                       "The project has an empty mapfile")

            test_sample = self.project.map[0]
            self.cond( test_sample._fields[0] == "SampleID",
                       "The project's map.txt does not have 'SampleID' "\
                       +"as the first column")
            self.cond( test_sample._fields[-1] == "Description",
                       "The project's map.txt does not have 'Description' "\
                       +"as the last column" )
            self.cond( hasattr(test_sample, "BarcodeSequence") is True,
                       "The project's map.txt has no 'BarcodeSequence' column")
        else:
            self.cond( True is True,
                       "" 
            )
            
        assert self.all_tests_passed()
        


