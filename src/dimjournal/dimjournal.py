#!/usr/bin/env python3

import base64
import datetime as dt
import io
import itertools
import json
import logging
import pickle
from pathlib import Path
from typing import List
from urllib.parse import urlparse

import numpy as np
import pymtpng
import undetected_chromedriver as webdriver
from bs4 import BeautifulSoup
from PIL import Image
from selenium.common.exceptions import InvalidCookieDomainException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from slugify import slugify
from tqdm import tqdm

_log = logging.getLogger("dimjournal")


class Constants:
    date_format = "%Y-%m-%d %H:%M:%S.%f"
    home_url = "https://www.midjourney.com/home/"
    app_url = "https://www.midjourney.com/app/"
    account_url = "https://www.midjourney.com/account/"
    api_url = "https://www.midjourney.com/api/app/recent-jobs/"
    session_token_cookie = "__Secure-next-auth.session-token"
    app_element_id = "app-root"
    account_element_id = "__NEXT_DATA__"
    job_details = ["id", "enqueue_time", "prompt"]
    user_json = Path("user.json")
    jobs_upscaled_json = Path("jobs_upscaled.json")
    cookies_pkl = Path("cookies.pkl")
    mj_download_image_js = """var callback=arguments[arguments.length-1];function getDataUri(e,n){var a=new XMLHttpRequest;a.onload=function(){var e=new FileReader;e.onloadend=function(){n(e.result)},e.readAsDataURL(a.response)},a.open("GET",e),a.responseType="blob",a.send()}getDataUri(document.querySelector("img").src,function(e){callback(e)});"""


def prev_day(date_string: str) -> str:
    """
    Calculate the date 90 days before the given date.

    Args:
        date_string (str): The date string in the format "%Y-%m-%d %H:%M:%S.%f".

    Returns:
        str: The date string 90 days before the given date.
    """
    date_obj = dt.datetime.strptime(date_string, Constants.date_format)
    prev_day_obj = date_obj - dt.timedelta(days=90)
    prev_day_string = prev_day_obj.strftime(Constants.date_format)

    return prev_day_string


class MidjourneyAPI:
    """
    A class to interact with the Midjourney API.

    Attributes:
        archive_folder (Path): The path to the archive folder.
        driver (webdriver.Chrome): The Chrome driver.
    """

    def __init__(self, driver: webdriver.Chrome, archive_folder: Path | str) -> None:
        """
        The constructor for the MidjourneyAPI class.

        Args:
            driver (webdriver.Chrome): The Chrome driver.
            archive_folder (Path | str): The path to the archive folder.
        """
        self.archive_folder = Path(archive_folder)
        self.driver = driver
        self.log_in()
        self.get_user_info()

    def log_in(self) -> bool:
        """
        Log in to the Midjourney API.

        Returns:
            bool: True if login is successful, False otherwise.
        """
    def load_cookies(self):
        self.cookies_path = Path(self.archive_folder, Constants.cookies_pkl)
        if self.cookies_path.is_file():
            cookies = pickle.load(open(self.cookies_path, "rb"))
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except InvalidCookieDomainException:
                    pass

    def save_cookies(self):
        pickle.dump(self.driver.get_cookies(), open(self.cookies_path, "wb"))

    def log_in(self) -> bool:
        self.load_cookies()
        try:
            self.driver.get(Constants.home_url)
            WebDriverWait(self.driver, 60 * 10).until(EC.url_to_be(Constants.app_url))
            WebDriverWait(self.driver, 60 * 10).until(
                EC.presence_of_element_located((By.ID, Constants.app_element_id))
            )
            cookie = self.driver.get_cookie(Constants.session_token_cookie)
            if cookie is not None:
                self.save_cookies()
                self.session_token = cookie["value"]
                return True
            else:
                return False
        except Exception as e:
            _log.error(f"Failed to get session token: {str(e)}")
            return False
    def load_user_info(self):
        self.user_info = {}
        self.user_json = Path(self.archive_folder, Constants.user_json)
        if self.user_json.is_file():
            self.user_info = json.loads(self.user_json.read_text())
        else:
            self.user_info = self.fetch_user_info()
            if self.user_info:
                self.user_json.write_text(json.dumps(self.user_info))

    def fetch_user_info(self):
        try:
            self.driver.get(Constants.account_url)
            WebDriverWait(self.driver, 60 * 10).until(
                EC.presence_of_element_located(
                    (By.ID, Constants.account_element_id)
                )
            )
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            script_tag_contents = soup.find(
                "script", id=Constants.account_element_id
            ).text
            return json.loads(script_tag_contents)
        except Exception as e:
            _log.error(f"Failed to get user info: {str(e)}")
            return None

    def get_user_info(self) -> bool:
        self.load_user_info()
        if self.user_info:
            self.user_id = self.user_info["props"]["pageProps"]["user"]["id"]
            return True
        else:
            return False

    def request_recent_jobs(
        self,
        from_date: str | None = None,
        page: int | None = None,
        job_type: str | None = None,
        amount: int = 50,
    ) -> List[dict]:
        """
        Request recent jobs from the Midjourney API.

        Args:
            from_date (str | None): The date from which to request jobs.
            page (int | None): The page number to request.
            job_type (str | None): The type of job to request.
            amount (int): The number of jobs to request.

        Returns:
            List[dict]: A list of jobs.
        """
        params = {}
        if from_date:
            pass  # params["fromDate"] = prev_day(from_date)
        if page:
            params["page"] = page
        if job_type:
            params["jobType"] = job_type
        params["amount"] = amount
        params["orderBy"] = "new"
        params["jobStatus"] = "completed"
        params["userId"] = self.user_id
        params["dedupe"] = "true"
        params["refreshApi"] = 0

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{Constants.api_url}?{query_string}"

        _log.debug(f"Requesting {url}")
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        pre_tag_contents = soup.find("pre").text
        job_listing = json.loads(pre_tag_contents)

        if isinstance(job_listing, list):
            if len(job_listing) > 0 and isinstance(job_listing[0], dict):
                if all(f in job_listing[0] for f in Constants.job_details):
                    _log.debug(f"Got job listing with {len(job_listing)} jobs")
                    return job_listing
                if job_listing[0] == {"msg": "No jobs found."}:
                    _log.debug(f"Response: 'No jobs found'")
                    return []
            elif len(job_listing) == 0:
                _log.debug(f"Response: 'No jobs found'")
                return []
        raise ValueError(job_listing)


class MidjourneyJobCrawler:
    def __init__(
        self, api: MidjourneyAPI, archive_folder: Path, job_type: str | None = None
    ):
        """
        The constructor for the MidjourneyJobCrawler class.

        Args:
            api (MidjourneyAPI): The Midjourney API.
            archive_folder (Path): The path to the archive folder.
            job_type (Optional[str]): The type of job to crawl.
        """
        self.api = api
        self.job_type = job_type
        self.archive_folder = archive_folder
        if job_type:
            self.archive_file = Path(f"jobs_{job_type}.json")
        else:
            self.archive_file = Path("jobs.json")
        self.archive_file = self.archive_folder / self.archive_file
        self.archive_data = []

    def load_archive_data(self):
        """
        Load the archive data.
        """
        if self.archive_file.is_file():
            self.archive_data = json.loads(self.archive_file.read_text())
        else:
            self.archive_data = []

    def update_archive_data(self, job_listing: List[dict]):
        """
        Update the archive data with the given job listing.

        Args:
            job_listing (List[dict]): The job listing.

        Returns:
            bool: True if the archive data was updated, False otherwise.
        """
        new_entries = [
            job
            for job in job_listing
            if job["id"] not in [x["id"] for x in self.archive_data]
        ]
        if new_entries:
            self.archive_data.extend(new_entries)
            self.archive_file.write_text(json.dumps(self.archive_data, indent=2))
        else:
            return False
        return True

    def crawl(
        self,
        limit: int | None = None,
        from_date: str | None = None,
    ):
        """
        Crawl the Midjourney API for job listings.

        Args:
            limit (Optional[int]): The maximum number of pages to crawl.
            from_date (Optional[str]): The date from which to start crawling.
        """
        job_str = self.job_type if self.job_type else "all"
        self.load_archive_data()
        pages = range(1, limit + 1) if limit else itertools.count(1)
        for page in tqdm(pages, desc=f"Crawling for {job_str} job info"):
            job_listing = self.api.request_recent_jobs(
                from_date=from_date, page=page, job_type=self.job_type
            )
            if not job_listing:
                _log.debug(
                    f"Empty {job_str} job listing batch: reached end of total job listing"
                )
                break
            if not self.update_archive_data(job_listing):
                _log.debug(f"No new {job_str} jobs found: stopping crawler")
                break
            if from_date is None:
                from_date = job_listing[0]["enqueue_time"]


class MidjourneyDownloader:
    def __init__(self, api, archive_folder):
        """
        The constructor for the MidjourneyDownloader class.

        Args:
            api (MidjourneyAPI): The Midjourney API.
            archive_folder (Path): The path to the archive folder.
        """
        self.api = api
        self.archive_folder = Path(archive_folder)
        self.archive_folder.mkdir(parents=True, exist_ok=True)
        self.jobs_json_path = Path(self.archive_folder, "jobs_upscale.json")
        self.jobs_upscale = self.read_jobs()

    def fetch_image(self, url):
        """
        Fetch an image from the given URL.

        Args:
            url (str): The URL of the image.

        Returns:
            Tuple[bytes, str]: The image data and the image type.
        """
        self.api.driver.get(url)
        data_uri = self.api.driver.execute_async_script(Constants.mj_download_image_js)
        header, encoded = data_uri.split(",", 1)
        image_type = header.split(";")[0].split("/")[-1]
        image_data = base64.b64decode(encoded)
        return image_data, image_type

    def read_jobs(self):
        """
        Read the job listings.

        Returns:
            List[dict]: The job listings.
        """
        with open(self.jobs_json_path, "r") as file:
            return json.load(file)

    def save_jobs(self):
        """
        Save the job listings.
        """
        with open(self.jobs_json_path, "w") as file:
            json.dump(self.jobs_upscale, file, indent=2)
        _log.debug(f"Updated {self.jobs_json_path}")

    def create_folders(self, dt_obj):
        """
        Create folders for the given date.

        Args:
            dt_obj (datetime): The date.

        Returns:
            Path: The path to the created folder.
        """
        dt_year = f"{dt_obj.year}"
        path_year = Path(self.archive_folder, dt_year)
        path_year.mkdir(parents=True, exist_ok=True)
        month = f"{dt_obj.month:02}"
        path_month = Path(path_year, month)
        path_month.mkdir(parents=True, exist_ok=True)
        return path_month

    def fetch_and_write_image(self, image_url, image_path, info):
        """
        Fetch an image from the given URL and write it to the given path.

        Args:
            image_url (str): The URL of the image.
            image_path (Path): The path to write the image.
            info (dict): The metadata of the image.

        Returns:
            bool: True if the image was successfully fetched and written, False otherwise.
        """
        if not image_path.is_file():
            image_data, image_type = self.fetch_image(image_url)
            if image_type == "png":
                try:
                    image_array = np.array(Image.open(io.BytesIO(image_data)))
                    with open(image_path, "wb") as fh:
                        pymtpng.encode_png(image_array, fh, info=info)
                except Exception as e:
                    _log.error(f"Fishy PNG: {image_url}")
                    with open(image_path, "wb") as fh:
                        fh.write(image_data)
            else:
                with open(image_path, "wb") as fh:
                    fh.write(image_data)
            return True
        else:
            return False

    def download_missing(self):
        """
        Download missing images.
        """

        with tqdm(total=len(self.jobs_upscale), desc="Downloading") as pbar:
            last_tick = 0
            for job_i, job in enumerate(self.jobs_upscale):
                if not job.get("arch", False):
                    dt_obj = dt.datetime.strptime(
                        job["enqueue_time"], Constants.date_format
                    )
                    path_month = self.create_folders(dt_obj)

                    dt_stamp = dt_obj.strftime("%Y%m%d-%H%M")
                    prompt = job.get("prompt", "") or job.get("full_command", "") or ""
                    image_url = job["image_paths"][0]

                    job["arch_prompt_slug"] = slugify(prompt)[:49]
                    path_base = (
                        f"""{dt_stamp}_{job["arch_prompt_slug"]}_{job["id"][:4]}"""
                    )
                    path_ext = Path(urlparse(image_url).path).suffix[1:]
                    image_path = Path(path_month, f"""{path_base}.{path_ext}""")
                    info = {
                        "Title": job.get("prompt", ""),
                        "Author": job.get("username", ""),
                        "Description": job.get("full_command", ""),
                        "Copyright": job.get("username", ""),
                        "Creation Time": job.get("enqueue_time", ""),
                        "Software": "Midjourney",
                    }
                    if self.fetch_and_write_image(image_url, image_path, info):
                        job["arch"] = True
                        job["arch_image_path"] = str(
                            image_path.relative_to(self.archive_folder)
                        )

                        pbar.set_description(f"{job['arch_image_path']}")
                        pbar.update(job_i + 1 - last_tick)
                        last_tick = job_i + 1
                        _log.debug(
                            f"""Saving {job["arch_image_path"]} from {image_url}"""
                        )
        self.save_jobs()


def download(
    archive_folder: Path | str | None = None,
    user_id: str | None = None,
    limit: int | None = None,
):
    """
    Download images from the Midjourney API.

    Args:
        archive_folder (Optional[Union[Path, str]]): The path to the archive folder.
        user_id (Optional[str]): The user ID.
        limit (Optional[int]): The maximum number of pages to download.
    """
    logging.basicConfig(level=logging.INFO)
    import os

    pictures_folder = "My Pictures" if os.name == "nt" else "Pictures"
    archive_folder = (
        Path(archive_folder)
        if archive_folder
        else Path(os.path.expanduser("~"), pictures_folder, "midjourney", "dimjournal")
    )
    if not archive_folder.is_dir():
        archive_folder.mkdir(parents=True)
    _log.info(f"Data will be saved in: {archive_folder}")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(use_subprocess=True, options=options)
    api = MidjourneyAPI(driver=driver, archive_folder=archive_folder)

    try:
        crawler = MidjourneyJobCrawler(api, archive_folder, job_type="upscale")
        crawler.crawl(limit=limit)
        crawler = MidjourneyJobCrawler(api, archive_folder, job_type=None)
        crawler.crawl(limit=limit)
        downloader = MidjourneyDownloader(api, archive_folder)
        downloader.download_missing()
    except KeyboardInterrupt:
        _log.warn("Caught KeyboardInterrupt")
    finally:
        driver.quit()
