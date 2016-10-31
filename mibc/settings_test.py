import os
import tempfile

testconfig = """
class foobaz(object):
    chumble = "spuzz"
"""


def test_settings():
    with tempfile.NamedTemporaryFile() as tmp_file:
        print >> tmp_file, testconfig
        tmp_file.seek(0)
        os.environ["MIBC_SETTINGS_FILE"] = tmp_file.name
        import settings
        assert settings.foobaz.chumble == "spuzz"
        
