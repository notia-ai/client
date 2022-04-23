from notia import apikey
from .display import Display
from .config import NOTIA_ENDPOINT, NOTIA_WEB


class _NotiaLogin:
    def __init__(self):
        self._api_url = NOTIA_ENDPOINT
        self._web_url = NOTIA_WEB
        self._key = None
        self._relogin = None
        self._display = Display()

    def setup(self, kwargs):
        self._relogin = kwargs.pop("relogin", None)

    def login(self):
        """
        Login checks is API key is configured, if not prompts user to input
        No actual logging in is done.
        """
        apikey_configured = self.is_apikey_configured()
        if self._relogin:
            apikey_configured = False
        if not apikey_configured:
            return False

        return apikey_configured

    def is_apikey_configured(self):
        return apikey.api_key_exists(self._api_url) is not None

    def configure_api_key(self, key):
        self._display.warning(
            (
                "If you are specifying your api key in code, ensure this code is"
                "not shared publically."
                "Consider setting the NOTIA_API_KEY environment variable"
            )
        )
        apikey.write_netrc(self._api_url, "user", key)
        self._key = key

    def prompt_api_key(self):
        key = apikey.prompt_api_key(self._web_url, self._api_url)
        self._key = key


def login(key=None, relogin=None):
    """
    Log in to Notia.
    Arguments:
        key: (string, optional) authentication key.
        relogin: (bool, optional) If true, will re-prompt for API key.
    Returns:
        bool: if key is configured
    Raises:
        UsageError - if api_key can not configured and no tty
    """
    kwargs = dict(locals())
    configured = _login(**kwargs)
    return True if configured else False


def _login(
    key=None,
    relogin=None,
):
    kwargs = dict(locals())

    nlogin = _NotiaLogin()

    nlogin.setup(kwargs)

    logged_in = nlogin.login()

    key = kwargs.get("key")
    if key:
        nlogin.configure_api_key(key)

    if logged_in:
        return logged_in

    if not key:
        nlogin.prompt_api_key()

    return nlogin._key or False
