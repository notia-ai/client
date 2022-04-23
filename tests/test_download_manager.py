import notia
import pytest
import responses
from responses import matchers
import os
import json
import uuid


@pytest.fixture(scope="module")
def base_config():
    return {"API_URL": os.environ.get("NOTIA_ENDPOINT", "https://notia.api.notia.ai")}


@pytest.fixture(scope="session")
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


def test_load_datasets(base_config, mocked_responses):
    API_URL = base_config["API_URL"]
    AWS_URL = (
        f"https://s3.eu-west-2.amazonaws.com/example-bucket/example/{uuid.uuid4()}"
    )
    params = {"slug": "XXXXXXXX"}

    mocked_responses.add(
        responses.GET,
        f"{API_URL}/api/datasets/presign",
        body=json.dumps({"url": AWS_URL}),
        status=200,
        match=[matchers.query_param_matcher(params)],
        content_type="application/json",
    )
    mocked_responses.add(
        responses.GET,
        f"{AWS_URL}",
        body=open("./resources/test.zip", "rb").read(),
        status=200,
        auto_calculate_content_length=True,
        content_type="multipart-form/data",
    )

    notia.load_dataset("XXXXXXXX", load=False)
