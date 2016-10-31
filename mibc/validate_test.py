
from pprint import pprint

import models
from tests import user_to_test, project_to_test
from validate import validate

class Validator_Test(object):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_repo(self):
        repo = models.Repository()
        l =  validate(repo)
        pprint(l)
        assert len(l) > 0

    def test_user(self):
        repo = models.Repository()
        user = repo.users[user_to_test]
        l = validate(user)
        pprint(l)
        assert len(l) > 0

    def test_project(self):
        repo = models.Repository()
        user = repo.users[user_to_test]
        project = user.projects[project_to_test]
        l = validate(project)
        pprint(l)
        assert len(l) > 0


if __name__ == '__main__':
    c = Validator_Test()
    c.test_repo()
    c.test_user()
    c.test_project()
