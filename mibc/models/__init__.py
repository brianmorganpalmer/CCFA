import os
from datetime import datetime

from .. import (
    util,
    settings
)

from . import (
    usermixins,
    projectmixins,
    mapping_file
)


default_repo = None
def default_Repository():
    global default_repo
    if default_repo is None:
        default_repo = Repository()

    return default_repo

            
class Repository(object):

    def __init__(self, path=settings.c_repository_root):
        self.path = path
        self.users = UserRoster(self)

        # first initialized repo is the default seems good to me
        global default_repo
        if default_repo is None:
            default_repo = self

        self._last_updated = None


    def newly_updated(self, since=datetime.now()):
        return [ 
            u for u in self.users.all() if since < u.last_updated 
            ]


    @property
    def last_updated(self):
        if not self._last_updated:
            self._last_updated = max( util.stat(self.path, f).st_mtime
                                      for f in os.listdir(self.path) )
            self._last_updated = datetime.fromtimestamp(self.last_updated)

        return self._last_updated


    def __eq__(self, other):
        return self.path == other.path
    
    def __str__(self):
        return "<Repository('%s')>" % self.path

    def __repr__(self):
        return "Repository"

    def __hash__(self):
        return hash(self.path)



class User(util.SerializableMixin, usermixins.LDAP):

    serializable_attrs = ['name', 'path', 'last_updated', 'projects']
    
    def __init__(self, name, repo=None, autopopulate=False):
        self.name = name
        self.repo = repo if repo is not None else default_Repository()

        self.path = os.path.join(self.repo.path, name)
        self.projects = ProjectRoster(self)

        self._last_updated = None

        
    def exists(self):
        return os.path.exists(self.path)

    def newly_updated(self, since=datetime.now()):
        return [ 
            p for p in self.projects.all() if since < p.last_updated 
            ]


    @property
    def last_updated(self):
        if not self._last_updated:
            self._last_updated = max( util.stat(self.path, f).st_mtime
                                      for f in os.listdir(self.path) )
            self._last_updated = datetime.fromtimestamp(self.last_updated)

        return self._last_updated

    @staticmethod
    def from_path(path):
        path_parts = os.path.split(os.path.realpath(os.path.abspath(path)))
        repo_str, user_str = path_parts
        return Repository(path=repo_str).users[user_str]

    def __str__(self):
        return "<User '%s'>" % self.name
                                 
    def __repr__(self):
        return "User"



class Project(util.SerializableMixin, projectmixins.validation):
    
    dont_belong_in_metadata = [ 'user', 'name', 'path', 'map', 'map_headers' ]

    def __init__(self, name, user, autopopulate=False):
        self.name = name
        self.user = user
        self.path = os.path.join(user.path, name)

        self._autopopulated = False
        if autopopulate:
            self.autopopulate()

        self._last_updated = None

        
    def exists(self):
        return os.path.exists(self.path) and self.user.exists()

    def _custom_serialize(self):
        if not self._autopopulated:
            self.autopopulate()
        return self._attrs()

    def _attrs(self):
        return dict( (key, val) 
                     for key, val in self.__dict__.iteritems()
                     if not key.startswith('_') )

    def _metadata_attrs(self):
        return dict( (key, val)
                     for key, val in self._attrs().iteritems()
                     if key not in self.dont_belong_in_metadata )

    @property
    def last_updated(self):
        if not self._last_updated:
            self._last_updated = max( util.stat(self.path, f).st_mtime
                                      for f in os.listdir(self.path) )
            self._last_updated = datetime.fromtimestamp(self._last_updated)

        return self._last_updated

    
    @staticmethod
    def from_path(path):
        rest, project_str = os.path.split(
            os.path.realpath(os.path.abspath(path)))
        repo_str, user_str = os.path.split(rest)
        return Repository(path=repo_str).users[user_str].projects[project_str]
        

    def save(self):
        with open(os.path.join(self.path, "metadata.txt"), 'w') as meta_file:
            util.serialize_tsv(self._metadata_attrs(), to_fp=meta_file)
        
        if self.map and self.map_headers:
	    with open(os.path.join(self.path, "map.txt"), 'w') as map_file:
                print >> map_file, "\t".join(self.map_headers)
                for record in self.map:
                    print >> map_file, "\t".join(record)
        elif self.filename:
	    with open(os.path.join(self.path, "map.txt"), 'w') as map_file:
                print >> map_file, "#SampleID"
                for f in self.filename:
                    name = util.rmext(os.path.basename(f))
                    print >> map_file, os.path.basename(name)


    def autopopulate(self):
        self.__dict__.update( self._gather('metadata.txt') )
        try:
            self.map = mapping_file.load('map.txt', basepath=self.path)
        except IOError:
            self.map = list()
        self.map_headers = self.map[0]._fields if self.map else list()

        self._autopopulated = True


    def _gather(self, filename):
        p = os.path.join(self.path, filename)
        with open(p) as f:
            return dict( (key, val)
                         for (key, val) in util.deserialize_tsv(f) 
                         if not hasattr(self, key) )


    def __getattr__(self, name):
        if not self._autopopulated:
            try:
                self.autopopulate()
                return getattr(self, name)
            except IOError as e:
                raise AttributeError( "Unable to retrieve %s: %s"%(name, e) )
        else:
            raise AttributeError(name)

    def __str__(self):
        return "<Project(%s, %s) >" % (self.user.name, self.name)

    def __repr__(self):
        return "Project"

    def __hash__(self):
        return hash(self.path)



class BaseRoster(util.SerializableMixin):

    parent = None

    def __init__(self, MemberClass):
        self.MemberClass = MemberClass


    def _custom_serialize(self):
        return [ f for f in os.listdir(self.parent.path)
                 if os.path.isdir(os.path.join(self.parent.path, f)) ]


    def get(self, key):
        return self.MemberClass( key, self.parent )


    def all(self):
        paths = [ os.path.abspath( os.path.join(self.parent.path, f) )
                  for f in os.listdir(self.parent.path) ]

        return [ self.MemberClass( os.path.basename(path),
                                   self.parent, 
                                   autopopulate=False )
                 for path in paths if os.path.isdir(path) \
                 and os.path.basename(path) not in settings.users.ignored ]


    def __getitem__(self, key):
        return self.get(key)



class ProjectRoster(BaseRoster):

    def __init__(self, user):
        self.MemberClass = Project
        self.parent = user


        
class UserRoster(BaseRoster):
    
    def __init__(self, repo):
        self.MemberClass = User
        self.parent = repo

