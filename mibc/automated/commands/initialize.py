"""Extra commands for initializing a project directory without using
the automatic metadata generator webform
"""
import os
import re
import sys
import glob
import logging
from collections import defaultdict

from doit.cmd_base import Command

from ...models import Project

true_strings = {
    "true": "true", 
    "yes":  "true",
    "y":    "true",
}

_project_dir = './'

IGNORED_FILES = [
    'metadata.txt', 'map.txt'
]


def choices(*selections):
    def wrapped(answer):
        answer = answer.lower()
        if answer in selections:
            return answer
        else:
            raise KeyError("`%s' not a valid choice. "
                           "Choices are %s"%(answer, str(selections)))

    return wrapped


def pattern_list_or_listdir(answer):
    if not answer:
        return filter(not_ignored, os.listdir(_project_dir))
    elif answer.startswith("glob:"):
        pattern = os.path.join(_project_dir,
                               answer.split("glob:")[1])
        files = map(os.path.basename, glob.glob(pattern))
        return filter(not_ignored, files)
    elif answer.startswith("re:"):
        matcher = lambda s: re.search(answer.split("re:")[1], s)
        files = filter(matcher, os.listdir(_project_dir))
        return filter(not_ignored, files)
    elif ',' in answer:
        return answer.split(',')
    else:
        return [answer]
    

def not_ignored(fname):
    """for use in filters; determines whether this file should be
    included in the 'filename' field in the metadata.txt file

    """
    return fname not in IGNORED_FILES and os.path.isfile(fname)


def true_or_false(answer):
    return true_strings.get(answer.lower()) or "false",


OPTIONAL_FIELDS = {
    'pi_first_name'            : str,
    'pi_last_name'             : str,
    'pi_contact_email'         : str,
    'lab_name'                 : str,
    'researcher_first_name'    : str,
    'researcher_last_name'     : str,
    'researcher_contact_email' : str,
    'collection_start_date'    : str,
    'collection_end_date'      : str,
    'submit_to_insdc'          : true_or_false,
    'reverse_primer'           : str,
    'skiptasks'                : str
}

REQUIRED_FIELDS = {
    'study_title'       : str,
    'study_description' : str,
    'sample_type'       : str,
    'filename'          : pattern_list_or_listdir,
    '16s_data'          : true_or_false,
    'visualize'         : true_or_false,
    'platform'          : choices("illumina", "454")
}

opt_dir = {"name": "dir",
           "short": "d",
           "long": "dir",
           "type": str,
           "default": "./",
           "help": "Where to initialize the project",}

opt_logging = {"name": "logging",
               "short": "l",
               "long": "logging",
               "type": str,
               "default": "WARNING",
               "help": ("Logging verbosity. Valid choices are "
                        "debug, info, warn, and critical"),}


opt_ignore = {"name": "ignore",
               "long": "ignore",
               "type": str,
               "default": "",
               "help": ("Comma separated list of files to ignore when"
                        " automatically ading file names to project"
                        " metadata"),}


class InitializeProject(Command):
    name = "initialize-project"
    doc_purpose = ('Initialize a MIBC project')
    doc_usage = '[[key:value] key:value]'
    doc_description = \
"""Initializes a MIBC project in the current directory,
or as specified by the -d or --dir options.
Arguments are key:value pairs for metadata records.
The user will be queried for any missing required metadata
fields.
"""

    cmd_options = (opt_dir, opt_logging, opt_ignore)

    def execute(self, opt_values, pos_args):
        self.logger = self._setup_logging(opt_values['logging'])

        project = Project.from_path(opt_values['dir'])
        # :wince:
        global _project_dir, IGNORED_FILES
        _project_dir = opt_values['dir']
        IGNORED_FILES.extend(
            f.strip() for f in opt_values['ignore'].split(',') if f
        )

        given_fields = self.parse_pos_args(pos_args)
        given_fields = self.merge_fields(given_fields)
        for f in REQUIRED_FIELDS:
            if f in given_fields:
                value = given_fields.pop(f)
            else:
                value = self.query_user_for_field(f)
            setattr(project, f, value)

        # now add the rest of the optional fields
        for f, value in given_fields.items():
            setattr(project, f, value)

        project.save()
                

    def _setup_logging(self, loglevel_str):
        l = logging.getLogger()
        l.setLevel(getattr(logging, loglevel_str.upper()))
        logging.basicConfig(format="%(levelname)s: %(message)s")
        return l


    def merge_fields(self, fields):
        fields_dict = defaultdict(list)
        for key, val in fields:
            if type(val) in (tuple, list):
                fields_dict[key].extend(val)
            else:
                fields_dict[key].append(val)
        return fields_dict


    def parse_pos_args(self, pos_args):
        index = REQUIRED_FIELDS.copy()
        index.update(OPTIONAL_FIELDS)
        for arg in pos_args:
            if ":" not in arg:
                self.logger.warn("Ill-formatted argument `%s'. "
                                 "Arguments should be formatted key:value", arg)
                continue
            key, val = arg.split(':', 1)
            val = val.strip()
            if key in index:
                try:
                    func = index[key]
                    yield key, func(val)
                except KeyError as e:
                    self.logger.warn(e)
                    continue
            else:
                self.logger.warn("Unrecognized key `%s'", key)
                continue


    def query_user_for_field(self, f):
        func = REQUIRED_FIELDS[f]
        answer = None
        while not answer:
            try:
                answer = raw_input("%s: "%(f)).strip()
                return func(answer)
            except (KeyboardInterrupt, EOFError):
                self.logger.warn("Skipping prompt for field `%s' "
                                 "on user interrupt", f)
                return
            except Exception as e:
                self.logger.warn(e)
                answer = None
