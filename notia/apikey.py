import os
from urllib.parse import urlparse
import textwrap
import stat
import getpass

from .display import Display
from rich.panel import Panel
from rich import box

display = Display()


def _find_netrc_api_key(url, raise_errors=False):
    NETRC_FILES = (".netrc", "_netrc")
    netrc_file = os.environ.get("NETRC")
    if netrc_file is not None:
        netrc_locations = (netrc_file,)
    else:
        netrc_locations = ("~/{}".format(f) for f in NETRC_FILES)

    try:
        from netrc import netrc, NetrcParseError

        netrc_path = None

        for f in netrc_locations:
            try:
                loc = os.path.expanduser(f)
            except KeyError:
                return

            if os.path.exists(loc):
                netrc_path = loc
                break

        if netrc_path is None:
            return

        ri = urlparse(url)

        host = ri.netloc.split(":")[0]

        try:
            _netrc = netrc(netrc_path).authenticators(host)
            if _netrc:
                login_i = 0 if _netrc[0] else 1
                return (_netrc[login_i], _netrc[2])
        except (NetrcParseError, IOError):
            if raise_errors:
                raise

    except (ImportError, AttributeError):
        pass


def prompt_api_key(web_url: str, api_url: str):
    api_prompt = Panel(
        (
            f"You can find your API key :key: in your browser"
            f" [blue underline bold][link={web_url}/authorize]here[/link][/blue underline bold] "
        ),
        box=box.ROUNDED,
    )
    display.log_styled(api_prompt, style="yellow")
    display.log(
        "Paste the API key from your profile and hit enter, or press ctrl+c to quit: "
    )
    api_key = getpass.getpass()
    write_netrc(api_url, "user", api_key)
    return api_key


def api_key_exists(api_url: str):
    auth = _find_netrc_api_key(api_url, True)
    key = None
    if auth:
        key = auth[-1]
    # Environment should take precedence
    if os.getenv("NOTIA_API_KEY"):
        key = os.environ["NOTIA_API_KEY"]
    return key


def write_netrc(host: str, entity: str, key: str):
    """Add our host and key to .netrc"""
    if len(key) != 40:
        display.error(
            f"API-key must be exactly 40 characters long: {key} ({len(key)} chars)"
        )
        return None
    try:
        normalized_host = urlparse(host).netloc.split(":")[0]
        if normalized_host != "localhost" and "." not in normalized_host:
            display.error(
                f"Host must be a url in the form https://some.address.com, received {host}"
            )
            return None
        display.log(
            (
                f"Appending key for {normalized_host} "
                f"to your netrc file: {os.path.expanduser('~/.netrc')}"
            )
        )
        machine_line = "machine %s" % normalized_host
        path = os.path.expanduser("~/.netrc")
        orig_lines = None
        try:
            with open(path) as f:
                orig_lines = f.read().strip().split("\n")
        except IOError:
            pass
        with open(path, "w") as f:
            if orig_lines:
                # delete this machine from the file if it's already there.
                skip = 0
                for line in orig_lines:
                    # we fix invalid netrc files with an empty host that we wrote before
                    # verifying host...
                    if line == "machine " or machine_line in line:
                        skip = 2
                    elif skip:
                        skip -= 1
                    else:
                        f.write("%s\n" % line)
            f.write(
                textwrap.dedent(
                    """\
            machine {host}
              login {entity}
              password {key}
            """
                ).format(host=normalized_host, entity=entity, key=key)
            )
        os.chmod(os.path.expanduser("~/.netrc"), stat.S_IRUSR | stat.S_IWUSR)
        return True
    except IOError:
        display.error("Unable to read ~/.netrc")
        return None
