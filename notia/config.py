from .api import API as InternalAPI
from .display import Display as InternalDisplay
import os

NOTIA_ENDPOINT = os.environ.get("NOTIA_ENDPOINT", "https://notia.api.notia.ai")
NOTIA_WEB = os.environ.get("NOTIA_WEB", "https://notia.ai")
Api = InternalAPI(api_url=NOTIA_ENDPOINT)
Display = InternalDisplay()

NOTIA_CACHE = "~/.cache/notia/datasets"
NOTIA_CACHE = os.path.expanduser(os.getenv("NOTIA_CACHE", NOTIA_CACHE))

EXTRACTED_DATASETS_DIR = "extracted"
DOWNLOADED_DATASETS_DIR = "downloads"
