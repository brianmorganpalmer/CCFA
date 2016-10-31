import logging
import optparse
from pprint import pprint

from .render import render_to_email

from .. import (
    models,
    settings
)
from ..validate import validate


DESCRIPTION="""%prog - run validation suite on a project and notify users"""

HELP="""
%prog [options] [<username>/<project> [<username>/<project> ... ]]
%prog [options] [<username> [<username> ... ]]

Examples: %prog example_user/example_project
          %prog -n example_user
"""

opts_list = [
    optparse.make_option('-n', '--dry-run', action="store_true", 
                         dest="dry_run",
                         help="Instead of emailing users, print the email."),
    optparse.make_option('-a', '--auto', action="store_true", 
                         dest="auto_mode",
                         help="Find and validate projects updated since last "+
                         "validation run"),
     optparse.make_option('-l', '--logging', action="store", type="string",
                         dest="logging", default="INFO",
                         help="Logging verbosity, options are debug, info, "+
                         "warning, and critical")
]

repo = models.Repository()

def _parse_path(*paths):
    project_set = set()
    for path in paths:
        path = path.split("/")
        user = repo.users[path[0]]
        if len(path) > 1:
            project = path[1]
            project_set.add( user.projects[project] )
        else:
            for project in user.projects.all():
                project_set.add( project )

    return list(project_set)

    
def _autodiscover_projects_to_validate():
    project_set = set()
    for user in repo.users.all():
        for project in user.projects.all():
            last_validated, validation_succeeded = project.validation_status
            if project.last_updated > last_validated:
                project_set.add(project)

    return list(project_set)
    

def _maybe_email_somebody( results_list, project, dry_run=False ):
    email = getattr(project, "researcher_contact_email", False)
    if not email:
        # Go get it from ldap. If even that fails, send it to the site
        # admin, and add another failed item in the results_list
        if 'mail' in project.user.ldap_attrs:
            email = project.user.ldap_attrs['mail']
        else:
            email = settings.email.default_from_addr
            results_list.append(
                'Project %s: cannot find user email from ldap' %(project.name)
            )

    context = dict( errors = results_list,
                    project = project )

    if dry_run:
        s = "Project %s Validation Results" %(project.name)
        print s
        print "-"*len(s)
        print "To: %s" %(email)
        pprint(context)
        print "-"*len(s)
        print
    else:
        render_to_email( context, list(email) )


def main():
    parser = optparse.OptionParser(option_list=opts_list, 
                                   usage=HELP,
                                   description=DESCRIPTION)
    (opts, args) = parser.parse_args()
    logging.getLogger().setLevel(getattr(logging, opts.logging.upper()))
    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s")

    if opts.auto_mode:
        projects_to_validate = _autodiscover_projects_to_validate()
    else:
        projects_to_validate = _parse_path(*args)

    if not projects_to_validate:
        logging.info("No projects found")

    for project in projects_to_validate:
        results = validate(project)
        results = set([ msg
                        for indicator, msg in results
                        if indicator is not True ])

        if not opts.dry_run:
            status = len(results) > 0
            project.validation_status = status

        if len(results) > 0:
            _maybe_email_somebody( list(results), project, opts.dry_run )
        else:
            logging.info("No issues found with project %s" %(project.name))


if __name__ == '__main__':
    main()
