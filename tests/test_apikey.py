from notia import apikey
import os


def test_write_netrc():
    api_key = "X" * 40
    res = apikey.write_netrc("http://localhost", "standard_user", api_key)
    assert res
    with open(os.path.expanduser("~/.netrc")) as f:
        assert (
            "machine localhost\n" "  login standard_user\n" "  password %s\n" % api_key
        ) in f.read()
