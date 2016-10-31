
from . import Repository

def test_ldap_attrs():
    user = Repository().users['kbayer']
    assert user.ldap_attrs['mail'][0] == "kb201b@gmail.com"

