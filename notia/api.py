from zipfile import BadZipfile
import requests
from typing import Optional
from notia.apikey import api_key_exists
from notia.models.dataset import DatasetMeta
from .display import Display


class API:
    """
    Class representing calls to the Notia.ai API
    """

    def __init__(self, api_url: str) -> None:
        self._session = requests.Session()
        self._api_url = api_url
        self._api_key = api_key_exists(self._api_url)
        self._display = Display()

    def Search(self, term=None) -> None:
        try:
            response = self._RequestUrl(
                self._api_url + "/datasets/filter", "GET", params={"search_query": term}
            )
            response_results = response.json()["results"]
            dataset_list = [
                DatasetMeta(**dataset["dataset"]) for dataset in response_results
            ]
            self._display.datasetsAsTable(dataset_list)
        except requests.exceptions.RequestException:
            self._display.error(
                (
                    "Failed to fetch search resulsts, please ensure you "
                    "have the correct login token, or contact support@notia.ai"
                )
            )
        except Exception as err:
            self._display.error(f"{err}")

    def Orders(self) -> None:
        try:
            response = self._RequestUrl(f"{self._api_url}/orders", "GET")
            self._display.ordersAsTable(response.json())
        except requests.exceptions.RequestException:
            self._display.error(
                (
                    "Failed to fetch user orders, please ensure you "
                    "have the correct login token, or contact support@notia.ai"
                )
            )
            raise

    def GetPresigned(self, slug: str) -> Optional[str]:
        request_url = self._api_url + "/api/datasets/presign"
        try:
            response = self._RequestUrl(request_url, "GET", params={"slug": slug})
            response.raise_for_status()
            presigned_url = response.json()["url"]
            return presigned_url
        except requests.exceptions.RequestException:
            self._display.error(
                (
                    "Failed to download dataset, please ensure you "
                    "have purchased this ID or contact support@notia.ai"
                )
            )
        except BadZipfile:
            self._display.error(
                (
                    "Error unzipping dataset, please manually inspect "
                    "the downloaded file or contact support@notia.ai"
                )
            )
            raise

    def _RequestUrl(
        self, url: str, verb: str, params: Optional[dict] = None, json=None
    ) -> requests.Response:
        if verb == "POST":
            return self._session.post(url, auth=(self._api_key, ""))
        elif verb == "GET":
            return self._session.get(url, params=params, auth=(self._api_key, ""))
        else:
            raise ValueError("Invalid HTTP operation provided")


def search(term=None) -> None:
    from .config import Api

    Api.Search(term)


def orders() -> None:
    from .config import Api

    Api.Orders()
