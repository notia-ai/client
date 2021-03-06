from zipfile import BadZipfile
import requests
from typing import Optional
from notia.apikey import api_key_exists
from notia.models.dataset import DatasetMeta
from notia.models import Order
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

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, new_key):
        self._api_key = new_key

    def Search(self, term=None, web_url=None) -> None:
        try:
            response = self._RequestUrl(
                self._api_url + "/datasets/filter", "GET", params={"search_query": term}
            )
            response_results = response.json()["results"]
            dataset_list = [
                DatasetMeta(**dataset["dataset"]) for dataset in response_results
            ]
            self._display.datasetsAsTable(dataset_list, web_url)
        except requests.exceptions.RequestException:
            self._display.error(
                (
                    "Failed to fetch search resulsts, please ensure you "
                    "have the correct login token, or contact support@notia.ai"
                )
            )
        except Exception as err:
            self._display.error(f"{err}")

    def Orders(self, web_url=None) -> None:
        try:
            response = self._RequestUrl(f"{self._api_url}/api/orders", "GET")
            order_list = [Order(**order) for order in response.json()]

            self._display.ordersAsTable(order_list, web_url)
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
    from .config import Api, NOTIA_WEB

    Api.Search(term, NOTIA_WEB)


def my_datasets() -> None:
    from .config import Api, NOTIA_WEB

    Api.Orders(NOTIA_WEB)
