import six
from operator import attrgetter

from anadama.commands import AnadamaCmdBase
from anadama.commands import Run
from anadama.commands import ListDag as AnadamaListDag
from anadama.commands import Help as AnadamaHelp
from anadama.commands import opt_runner, opt_tmpfiles

from ..loader import ProjectLoader

from .initialize import InitializeProject

opt_project = dict(
    name  = "project",
    short = "P",
    long  = "project",
    default = "project",
    help = "Path to the project to build",
    type=str
)

class ProjectCmdBase(AnadamaCmdBase):

    def execute(self, *args, **kwargs):
        self._loader = ProjectLoader()
        return super(ProjectCmdBase, self).execute(*args, **kwargs)
        
class RunProject(ProjectCmdBase, Run):
    my_opts = (opt_project, opt_runner)
    doc_purpose = "run a project locally"
    doc_usage   = "--project <project_dir>/ [TASK ...]"

class ListDag(ProjectCmdBase, AnadamaListDag):
    my_opts = (opt_project, opt_runner, opt_tmpfiles)
    doc_usage = "--project <project_dir> [TASK ...]"

class Help(AnadamaHelp):

    @staticmethod
    def print_usage(cmds):
        """Print mibc_build usage instructions"""
        print("MIBC Project build tool -- https://bitbucket.org/biobakery/ccfa")
        print('')
        print("Commands")
        for cmd in sorted(six.itervalues(cmds), key=attrgetter('name')):
            six.print_("  mibc_build %s \t\t %s" % (cmd.name, cmd.doc_purpose))
        print("")
        print("  mibc_build help              show help / reference")
        print("  mibc_build help task         show help on task fields")
        print("  mibc_build help <command>    show command usage")
        print("  mibc_build help <task-name>  show task usage")


all = (RunProject, ListDag, InitializeProject, Help)
