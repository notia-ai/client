from typing import Optional
import requests

from .display import Display
import time
from pathlib import Path
import os
import copy
import pandas as pd
from rich.progress import track
import tempfile
from functools import partial
from zipfile import BadZipfile, ZipFile
import shutil
import json
from .config import NOTIA_CACHE, Api, EXTRACTED_DATASETS_DIR, DOWNLOADED_DATASETS_DIR


class DownloadManager:
    """A class for managing caching & downloads from Notia.ai"""

    def __init__(self) -> None:
        self._display = Display()
        # cache_dir ~/.cache/notia/datasets
        self.cache_dir = NOTIA_CACHE
        # downloads_dir ~/.cache/notia/datasets/downloads
        self.downloads_dir = os.path.join(self.cache_dir, DOWNLOADED_DATASETS_DIR)
        # extract_dir ~/.cache/notia/datasets/extracted
        self.extract_dir = os.path.join(self.cache_dir, EXTRACTED_DATASETS_DIR)

    def get_from_cache(self, slug: str, force_download=False):
        if self.cache_dir is None:
            self.cache_dir = NOTIA_CACHE

        if isinstance(self.cache_dir, Path):
            self.cache_dir = str(self.cache_dir)

        os.makedirs(self.cache_dir, exist_ok=True)

        cache_path = os.path.join(self.cache_dir, slug)

        if os.path.exists(cache_path) and not force_download:
            return cache_path

        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.downloads_dir, exist_ok=True)

        temp_file_manager = partial(
            tempfile.NamedTemporaryFile, dir=self.downloads_dir, delete=False
        )

        try:
            with temp_file_manager() as temp_file:
                self.download_from_s3(temp_file, slug)
                shutil.move(temp_file.name, os.path.join(self.downloads_dir, slug))
                temp_file.close()
        except requests.exceptions.RequestException:
            # propagate upwards
            raise

        # extract the file from the download dir to the extract dir
        self.extract(
            os.path.join(self.downloads_dir, slug), os.path.join(self.extract_dir, slug)
        )

        shutil.move(os.path.join(self.extract_dir, slug), cache_path)
        os.remove(os.path.join(self.downloads_dir, slug))
        return cache_path

    def extract(self, input_path: str, output_path: str):
        try:
            os.makedirs(output_path, exist_ok=True)
            with ZipFile(input_path, "r") as zip_file:
                zip_file.extractall(path=output_path)
                zip_file.close()
        except BadZipfile:
            # propagate upwards
            raise

    def download_from_s3(self, temp_file, slug: str) -> None:
        presigned_url = Api.GetPresigned(slug)
        if presigned_url is not None:
            self._display.log(
                (
                    f"{slug} not found in cache or force_download set to True,"
                    f"downloading to {temp_file.name}"
                )
            )
            self.http_get(presigned_url, temp_file)
        else:
            raise ValueError(f"Unable to fetch resource at {slug}")

    def http_get(
        self, url, temp_file, resume_size=0, headers=None, timeout=100.0, max_retries=0
    ):
        headers = copy.deepcopy(headers) or {}
        if resume_size > 0:
            headers["Range"] = f"bytes={resume_size:d}-"
        response = self.request_with_retry(
            method="GET",
            url=url,
            max_retries=max_retries,
            timeout=timeout,
        )
        if response.status_code == 416:  # Range not satisfiable
            return

        content_length = response.headers.get("Content-Length")
        total = (
            resume_size + int(content_length) if content_length is not None else None
        )
        for chunk in track(
            response.iter_content(chunk_size=1024),
            description="Downloading...",
            total=total,
        ):
            if chunk:  # filter out keep-alive new chunks
                temp_file.write(chunk)

    def request_with_retry(
        self,
        method: str,
        url: str,
        max_retries: int = 0,
        base_wait_time: float = 0.5,
        max_wait_time: float = 2,
        timeout: float = 10.0,
        **params,
    ) -> requests.Response:
        """Wrapper around requests to retry in case it fails with a
           ConnectTimeout, with exponential backoff.

        Args:
            method (str): HTTP method, such as 'GET' or 'HEAD'.
            url (str): The URL of the resource to fetch.
            max_retries (int): Maximum number of retries, defaults to
                               0 (no retries).
            base_wait_time (float): Duration (in seconds) to wait before
                                    retrying the first time. Wait time between
                                    retries then grows exponentially,
                                    capped by max_wait_time.
            max_wait_time (float): Maximum amount of time between
                                   two retries, in seconds.
            **params: Params to pass to :obj:`requests.request`.
        """
        tries, success = 0, False
        while not success:
            tries += 1
            try:
                response = requests.request(
                    method=method.upper(), url=url, timeout=timeout, **params
                )
                success = True
            except (
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError,
            ) as err:
                if tries > max_retries:
                    raise err
                else:
                    self._display.log(
                        (
                            f"{method} request to {url} timed out,"
                            "retrying... [{tries/max_retries}]"
                        )
                    )
                    sleep_time = min(
                        max_wait_time, base_wait_time * 2 ** (tries - 1)
                    )  # Exponential backoff
                    time.sleep(sleep_time)
        return response


def _handle_tsv(tsv_path: str):
    return pd.read_csv(tsv_path, sep="\t")


def _handle_csv(csv_path: str):
    return pd.read_csv(csv_path)


def _handle_json(json_path: str):
    return json.loads(json_path)


def _handle_split(local_path: str, ext: str, split: str):
    fpath = os.path.join(local_path, split)
    print(fpath)
    if os.path.exists(f"{fpath}.csv"):
        return _handle_csv(f"{fpath}.csv")
    elif os.path.exists(f"{fpath}.tsv"):
        return _handle_tsv(f"{fpath}.tsv")
    elif os.path.exists(f"{fpath}.json"):
        return _handle_json(f"{fpath}.json")
    else:
        raise ValueError(
            (
                f"Load was true but {ext} was provided. Notia can automatically "
                "load CSV, JSON or TSV files. Please set load=False and manually "
                "load the file."
            )
        )


def load_dataset(ID: str, split: Optional[str] = None, load: Optional[bool] = True):
    download_manager = DownloadManager()
    local_path = download_manager.get_from_cache(ID)
    if not load:
        return local_path

    if split:
        # this should know the ext
        return _handle_split(local_path, "", split)
    else:
        datasets = []
        for file in os.listdir(local_path):
            # we pass the local path and the file stem so we can match on ext
            datasets.append(
                _handle_split(local_path, Path(file).suffix, Path(file).stem)
            )
        if len(datasets) == 1:
            # no need to tuple if single elem
            return datasets[0]
        else:
            return tuple(datasets)
