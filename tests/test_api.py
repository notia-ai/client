import notia
import pytest
import responses
from responses import matchers
import os


@pytest.fixture(scope="module")
def base_config():
    return {"API_URL": os.environ.get("NOTIA_ENDPOINT", "https://notia.api.notia.ai")}


@pytest.fixture(scope="session")
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


def test_search(base_config, mocked_responses):
    API_URL = base_config["API_URL"]
    params = {"search_query": "hello"}
    mocked_responses.add(
        responses.GET,
        f"{API_URL}/datasets/filter",
        body="{}",
        status=200,
        match=[matchers.query_param_matcher(params)],
        content_type="application/json",
    )

    notia.search("hello")


def test_orders(base_config, mocked_responses):
    API_URL = base_config["API_URL"]
    mocked_responses.add(
        responses.GET,
        f"{API_URL}/api/orders",
        body="{}",
        status=200,
        content_type="application/json",
    )

    notia.my_datasets()
