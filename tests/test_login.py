import notia
from notia import config
import pytest


@pytest.fixture(scope="session")
def notia_api():
    return notia.api.API(api_url=config.NOTIA_ENDPOINT)
