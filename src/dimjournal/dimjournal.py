#!/usr/bin/env python3

import base64
import datetime as dt
import io
import itertools
import json
import logging
import pickle
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import pymtpng
import undetected_chromedriver as webdriver
from bs4 import BeautifulSoup
from PIL import Image
from selenium.common.exceptions import InvalidCookieDomainException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from slugify import slugify
from tqdm import tqdm

_log = logging.getLogger("dimjournal")


class Constants:
    """
    A class to hold various constant values used throughout the Dimjournal application.

    These constants include URLs for Midjourney services, element IDs for web scraping,
    file names for data storage, and JavaScript snippets for browser automation.
    """
    date_format: str = "%Y-%m-%d %H:%M:%S.%f"
    home_url: str = "https://www.midjourney.com/home/"
    app_url: str = "https://www.midjourney.com/app/"
    account_url: str = "https://www.midjourney.com/account/"
    api_url: str = "https://www.midjourney.com/api/app/recent-jobs/"
    session_token_cookie: str = "__Secure-next-auth.session-token"
    app_element_id: str = "app-root"
    account_element_id: str = "__NEXT_DATA__"
    job_details: list[str] = ["id", "enqueue_time", "prompt"]
    user_json: Path = Path("user.json")
    jobs_upscaled_json: Path = Path("jobs_upscaled.json")
    cookies_pkl: Path = Path("cookies.pkl")
    mj_download_image_js: str = (
        "var callback=arguments[arguments.length-1];"
        "function getDataUri(e,n){"
        'var a=new XMLHttpRequest;a.onload=function(){var e=new FileReader;e.onloadend=function(){n(e.result)},e.readAsDataURL(a.response)},a.open("GET",e),a.responseType="blob",a.send()'  # noqa: E501
        "}"
        'getDataUri(document.querySelector("img").src,function(e){callback(e)});'
    )


def get_date_ninety_days_prior(date_string: str) -> str:
    """
    Get the date 90 days prior to the given date.

    Args:
        date_string (str): The date string in the format "%Y-%m-%d %H:%M:%S.%f".

    Returns:
        str: The date string 90 days prior to the given date.
    """
    DAYS_PRIOR = 90
    date_obj = dt.datetime.strptime(date_string, Constants.date_format)
    prev_day_obj = date_obj - dt.timedelta(days=DAYS_PRIOR)
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

    def load_cookies(self) -> None:
        """
        Loads cookies from a pickle file and adds them to the WebDriver.
        Cookies are used to maintain the user's session with Midjourney.
        """
        self.cookies_path: Path = Path(self.archive_folder, Constants.cookies_pkl)
        if self.cookies_path.is_file():
            try:
                cookies: list[dict] = pickle.load(open(self.cookies_path, "rb"))
                for cookie in cookies:
                    try:
                        # Attempt to add each cookie to the driver
                        self.driver.add_cookie(cookie)
                    except InvalidCookieDomainException:
                        # This exception can occur if the cookie's domain is not valid for the current URL.
                        # It's often safe to ignore for session cookies that will be valid once the correct domain is navigated to.
                        _log.debug(f"Invalid cookie domain for cookie: {cookie.get('name')}")
                        pass
            except Exception as e:
                _log.error(f"Error loading cookies from {self.cookies_path}: {str(e)}", exc_info=True)
        else:
            _log.info(f"No cookies file found at {self.cookies_path}. A fresh login may be required.")

    def save_cookies(self) -> None:
        """
        Saves the current WebDriver cookies to a pickle file.
        This preserves the session for future runs, avoiding repeated manual logins.
        """
        try:
            pickle.dump(self.driver.get_cookies(), open(self.cookies_path, "wb"))
            _log.info(f"Cookies saved to {self.cookies_path}")
        except Exception as e:
            _log.error(f"Error saving cookies to {self.cookies_path}: {str(e)}", exc_info=True)

    def log_in(self) -> bool:
        """
        Log in to the Midjourney API.

        Returns:
            bool: True if login is successful, False otherwise.
        """
        self.load_cookies()
        try:
            _log.info(f"Attempting to log in to Midjourney: {Constants.home_url}")
            self.driver.get(Constants.home_url)
            WebDriverWait(self.driver, 60 * 10).until(EC.url_to_be(Constants.app_url))
            _log.info(f"Successfully navigated to app URL: {Constants.app_url}")
            WebDriverWait(self.driver, 60 * 10).until(
                EC.presence_of_element_located((By.ID, Constants.app_element_id))
            )
            _log.info(f"App element located: {Constants.app_element_id}")
            cookie = self.driver.get_cookie(Constants.session_token_cookie)
            if cookie is not None:
                self.save_cookies()
                self.session_token = cookie["value"]
                _log.info("Successfully logged in and obtained session token.")
                return True
            else:
                _log.error("Failed to obtain session token cookie after navigation.")
                return False
        except TimeoutException:
            _log.error("Timeout during login: page navigation or element presence.")
            return False
        except Exception as e:
            _log.error(f"Unexpected error during login: {str(e)}", exc_info=True)
            return False

    def load_user_info(self) -> None:
        """
        Loads user information from a local JSON file if it exists,
        otherwise fetches it from Midjourney and saves it.
        """
        self.user_info: dict = {}
        self.user_json: Path = Path(self.archive_folder, Constants.user_json)
        if self.user_json.is_file():
            try:
                self.user_info = json.loads(self.user_json.read_text())
                _log.info(f"Loaded user data from {self.user_json}")
            except json.JSONDecodeError as e:
                _log.error(
                    f"Error decoding user info JSON from {self.user_json}: {str(e)}. "
                    "Attempting to re-fetch.",
                    exc_info=True,
                )
                self.user_info = self.fetch_user_info()
                if self.user_info:
                    self.user_json.write_text(json.dumps(self.user_info, indent=2))
                    _log.info(f"Saved newly fetched user info to {self.user_json}")
            except Exception as e:
                _log.error(
                    f"Unexpected error loading user info from {self.user_json}: {str(e)}",
                    exc_info=True,
                )
        else:
            _log.info(f"User info file not found at {self.user_json}. Fetching new data.")
            self.user_info = self.fetch_user_info()
            if self.user_info:
                try:
                    self.user_json.write_text(json.dumps(self.user_info, indent=2))
                    _log.info(f"Saved newly fetched user info to {self.user_json}")
                except IOError as e:
                    _log.error(
                        f"Error writing user info to {self.user_json}: {str(e)}",
                        exc_info=True,
                    )
            else:
                _log.warning("Failed to fetch user info. User ID may not be available.")

    def fetch_user_info(self) -> dict | None:
        """
        Navigates to the Midjourney account page and extracts user information
        from the embedded JSON data.

        This method uses BeautifulSoup to parse the HTML and locate the script tag
        containing the user data. It handles potential timeouts and JSON decoding errors.

        Returns:
            dict | None: A dictionary containing user information if successful, otherwise None.
        """
        try:
            _log.info(f"Fetching user info from {Constants.account_url}")
            self.driver.get(Constants.account_url)
            # Wait for the specific script element to be present on the page
            WebDriverWait(self.driver, 60 * 10).until(
                EC.presence_of_element_located((By.ID, Constants.account_element_id))
            )
            _log.info(
                f"Account page loaded, element {Constants.account_element_id} found."
            )
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            script_tag = soup.find("script", id=Constants.account_element_id)
            if not script_tag:
                _log.error(
                    f"Script tag ID {Constants.account_element_id} not found "
                    "on account page."
                )
                return None
            script_tag_contents = script_tag.text
            user_data: dict = json.loads(script_tag_contents)
            _log.info("Successfully fetched and parsed user info.")
            return user_data
        except TimeoutException:
            _log.error(
                f"Timeout waiting for account page elements: {Constants.account_url}"
            )
            return None
        except json.JSONDecodeError as e:
            _log.error(
                f"Error decoding JSON from account page script: {str(e)}",
                exc_info=True,
            )
            return None
        except Exception as e:
            _log.error(f"Unexpected error fetching user info: {str(e)}", exc_info=True)
            return None

    def get_user_info(self) -> bool:
        """
        Retrieves the user ID from the loaded user information.

        This method assumes `load_user_info` has already been called and populated
        `self.user_info`. It navigates through the nested dictionary structure
        to extract the user's ID.

        Returns:
            bool: True if the user ID is successfully obtained, False otherwise.
        """
        self.load_user_info()
        # Check for the presence of nested keys to safely access the user ID
        if (
            self.user_info
            and "props" in self.user_info
            and "pageProps" in self.user_info["props"]
            and "user" in self.user_info["props"]["pageProps"]
            and "id" in self.user_info["props"]["pageProps"]["user"]
        ):
            self.user_id: str = self.user_info["props"]["pageProps"]["user"]["id"]
            _log.info(f"User ID {self.user_id} obtained from user info.")
            return True
        else:
            _log.error(
                "User ID not found in user info structure. User info: %s",
                self.user_info,
            )  # Consider redacting self.user_info in logs if sensitive
            return False

    def request_recent_jobs(
        self,
        from_date: str | None = None,
        page: int | None = None,
        job_type: str | None = None,
        amount: int = 50,
    ) -> list[dict]:
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
        try:
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
                        _log.debug("Response: 'No jobs found'")
                        return []
                elif len(job_listing) == 0:
                    _log.debug("Response: 'No jobs found'")
                    return []
                _log.error(
                    f"Unexpected job listing format. Expected list, got "
                    f"{type(job_listing)}. Content: {job_listing}"
                )
                raise ValueError(f"Unexpected job listing format: {job_listing}")
            else:
                _log.error(
                    f"Unexpected job listing format. Expected list, got "
                    f"{type(job_listing)}. Content: {job_listing}"
                )
                raise ValueError(f"Unexpected job listing format: {job_listing}")
        except json.JSONDecodeError as e:
            content_snippet = (
                pre_tag_contents[:500] if "pre_tag_contents" in locals() else "N/A"
            )
            _log.error(
                f"JSON decode error from API: {str(e)}. Content: {content_snippet}...",
                exc_info=True,
            )
            return []
        except TimeoutException:
            _log.error(f"Timeout requesting recent jobs from {url}", exc_info=True)
            return []
        except Exception as e:
            _log.error(
                f"Unexpected error requesting recent jobs: {str(e)}", exc_info=True
            )
            return []


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
        try:
            if self.archive_file.is_file():
                _log.info(f"Loading archive data from {self.archive_file}")
                self.archive_data = json.loads(self.archive_file.read_text())
            else:
                _log.info(f"Archive {self.archive_file} not found. Starting fresh.")
                self.archive_data = []
        except json.JSONDecodeError as e:
            _log.error(
                f"Error decoding {self.archive_file}: {str(e)}. Starting fresh.",
                exc_info=True,
            )
            self.archive_data = []
        except Exception as e:
            _log.error(
                f"Failed to load {self.archive_file}: {str(e)}. Starting fresh.",
                exc_info=True,
            )
            self.archive_data = []

    def update_archive_data(self, job_listing: list[dict]):
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
            try:
                self.archive_file.write_text(json.dumps(self.archive_data, indent=2))
                _log.info(
                    f"Updated {self.archive_file} with {len(new_entries)} new entries."
                )
            except IOError as e:
                _log.error(
                    f"Failed to write to {self.archive_file}: {str(e)}", exc_info=True
                )
                return False  # IO error during save
        else:
            _log.debug("No new entries to add to the archive.")
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
                _log.debug(f"Empty {job_str} job listing: end of history.")
                break
            if not self.update_archive_data(job_listing):
                _log.debug(f"No new {job_str} jobs found, stopping crawler.")
                break
            # Update from_date to potentially optimize next request,
            # though current API usage doesn't seem to use it for paging.
            if from_date is None and job_listing:
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
        try:
            self.archive_folder.mkdir(parents=True, exist_ok=True)
            _log.info(f"Archive folder set to: {self.archive_folder}")
        except OSError as e:
            _log.error(
                f"Error creating archive folder {self.archive_folder}: {str(e)}",
                exc_info=True,
            )
            # This is critical, should probably raise or handle more gracefully
            # For now, proceeding may lead to errors if path is unusable.
        self.jobs_json_path = self.archive_folder / "jobs_upscale.json"
        self.jobs_upscale = self.read_jobs()

    def fetch_image(self, url):
        """
        Fetch an image from the given URL.

        Args:
            url (str): The URL of the image.

        Returns:
            Tuple[bytes, str]: The image data and the image type.
        """
        try:
            _log.debug(f"Fetching image from URL: {url}")
            self.api.driver.get(url)
            # Consider adding WebDriverWait for an element if image loading is slow
            data_uri = self.api.driver.execute_async_script(
                Constants.mj_download_image_js
            )
            if not data_uri or "," not in data_uri:
                _log.error(f"Invalid data URI from JS for {url}. Received: {data_uri}")
                return None, None
            header, encoded = data_uri.split(",", 1)
            image_type = header.split(";")[0].split("/")[-1]  # type: ignore
            image_data = base64.b64decode(encoded)
            _log.debug(f"Fetched image: type {image_type}, size {len(image_data)}B.")
            return image_data, image_type
        except TimeoutException:
            _log.error(f"Timeout fetching image from {url}", exc_info=True)
            return None, None
        except Exception as e:
            _log.error(
                f"Unexpected error fetching image from {url}: {e!s}", exc_info=True
            )
            return None, None

    def read_jobs(self):
        """
        Read the job listings.

        Returns:
            List[dict]: The job listings.
        """
        with open(self.jobs_json_path) as file:
            return json.load(file)

    def save_jobs(self):
        """
        Save the job listings.
        """
        try:
            _log.info(f"Saving {len(self.jobs_upscale)} jobs to {self.jobs_json_path}")
            with open(self.jobs_json_path, "w") as file:
                json.dump(self.jobs_upscale, file, indent=2)
            _log.info(f"Successfully saved jobs to {self.jobs_json_path}")
        except IOError as e:
            _log.error(
                f"Failed to write jobs to {self.jobs_json_path}: {str(e)}",
                exc_info=True,
            )
        except Exception as e:
            _log.error(
                f"Unexpected error saving jobs to {self.jobs_json_path}: {str(e)}",
                exc_info=True,
            )

    def create_folders(self, dt_obj):
        """
        Create folders for the given date.

        Args:
            dt_obj (datetime): The date.

        Returns:
            Path: The path to the created folder.
        """
        try:
            dt_year = f"{dt_obj.year}"
            path_year = Path(self.archive_folder, dt_year)
            path_year.mkdir(parents=True, exist_ok=True)

            month = f"{dt_obj.month:02}"
            path_month = Path(path_year, month)
            path_month.mkdir(parents=True, exist_ok=True)
            _log.debug(f"Ensured directory exists: {path_month}")
            return path_month
        except OSError as e:
            _log.error(
                f"Error creating directory for {dt_obj}: {str(e)}", exc_info=True
            )
            # Fallback to base archive_folder; images won't be organized by date.
            return self.archive_folder

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
        if image_path.is_file():
            _log.debug(f"Image already exists, skipping: {image_path}")
            return False

        image_data, image_type = self.fetch_image(image_url)
        if not image_data or not image_type:
            _log.error(f"Failed to fetch image data/type for {image_url}")
            return False

        try:
            if image_type == "png":
                try:
                    image_array = np.array(Image.open(io.BytesIO(image_data)))
                    with open(image_path, "wb") as fh:
                        pymtpng.encode_png(image_array, fh, info=info)
                except Exception:
                    _log.error(f"Fishy PNG: {image_url}")
                    with open(image_path, "wb") as fh:
                        pymtpng.encode_png(img_array, fh, info=info)
                    _log.info(f"Saved PNG w/ metadata: {image_path}")
                except Exception as e_png:
                    log_msg = (  # noqa: E501
                        f"Could not process PNG w/ pymtpng (URL: {image_url}, "
                        f"Path: {image_path}): {str(e_png)}. "  # noqa: E501
                        "Writing raw bytes instead."
                    )
                    _log.warning(log_msg, exc_info=True)
                    with open(image_path, "wb") as fh:  # Fallback
                        fh.write(image_data)
                    _log.info(f"Saved raw PNG data after error: {image_path}")
            else:  # For non-PNG images (jpg, webp, etc.)
                with open(image_path, "wb") as fh:
                    fh.write(image_data)
                _log.info(f"Saved {image_type.upper()} image: {image_path}")
            return True
        except IOError as e_io:
            _log.error(f"IOError writing to {image_path}: {str(e_io)}", exc_info=True)
            return False
        except Exception as e_general:
            _log.error(
                f"Unexpected error writing to {image_path}: {str(e_general)}",
                exc_info=True,
            )
            return False

    def download_missing(self):
        """
        Download missing images.
        """
        if not self.jobs_upscale:
            _log.info("No upscale jobs found to download.")
            return

        with tqdm(
            total=len(self.jobs_upscale), desc="Downloading missing images"
        ) as pbar:
            last_tick = 0
            for job_i, job in enumerate(self.jobs_upscale):
                if job.get("arch", False):
                    pbar.update(1)
                    last_tick = job_i + 1
                    continue

                try:
                    if not (job.get("enqueue_time") and job.get("image_paths")):
                        job_id = job.get("id", "N/A")  # noqa: E231
                        if not job.get("enqueue_time"):
                            _log.warning(
                                f"Skipping job {job_id} (missing enqueue_time)"
                            )
                        if not job.get("image_paths"):
                            _log.warning(f"Skipping job {job_id} (missing image_paths)")
                        pbar.update(1)
                        last_tick = job_i + 1
                        continue

                    dt_obj = dt.datetime.strptime(
                        job["enqueue_time"], Constants.date_format
                    )
                    path_month = self.create_folders(dt_obj)

                    dt_stamp = dt_obj.strftime("%Y%m%d-%H%M")
                    prompt = job.get("prompt", "") or job.get("full_command", "") or ""
                    image_url = job["image_paths"][0]

                    job["arch_prompt_slug"] = slugify(prompt)[:49]
                    path_base = f"{dt_stamp}_{job['arch_prompt_slug']}_{job['id'][:4]}"
                    path_ext = Path(urlparse(image_url).path).suffix[1:]
                    image_path = path_month / f"{path_base}.{path_ext}"
                    info = {
                        "Title": prompt,
                        "Author": job.get("username", "Unknown"),
                        "Description": job.get("full_command", prompt),
                        "Copyright": job.get("username", "Unknown"),
                        "Creation Time": job.get("enqueue_time", ""),
                        "Software": "Midjourney via Dimjournal",
                    }

                    if self.fetch_and_write_image(image_url, image_path, info):
                        job["arch"] = True
                        job["arch_image_path"] = str(
                            image_path.relative_to(self.archive_folder)
                        )
                        _log.info(f"Archived: {job['arch_image_path']}")
                        pbar.set_description_str(
                            f"Archived: {job['arch_image_path']}", refresh=True
                        )
                    else:
                        job_id = job.get("id", "N/A")
                        _log.warning(
                            f"Failed to archive for job {job_id} from {image_url}"
                        )
                        pbar.set_description_str(f"Failed: {job_id}", refresh=True)

                except (
                    dt.datetime.strptime
                ) as e_date:  # Python 3.10 specific type hint for strptime
                    job_id = job.get("id", "N/A")
                    time_str = job.get("enqueue_time", "")
                    _log.error(
                        f"Date parse error for job {job_id} ('{time_str}'): {e_date}",
                        exc_info=True,
                    )
                except KeyError as e_key:
                    job_id = job.get("id", "N/A")
                    _log.error(
                        f"Missing key in job data for {job_id}: {e_key}", exc_info=True
                    )
                except Exception as e_loop:
                    job_id = job.get("id", "N/A")
                    _log.error(
                        f"Unexpected error processing job {job_id}: {str(e_loop)}",
                        exc_info=True,
                    )
                finally:
                    pbar.update(job_i + 1 - last_tick)
                    last_tick = job_i + 1
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
    # Configure logging at the beginning of the function or module
    # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # If logging is configured globally (e.g. in __main__ or __init__), this line might not be needed here.
    # For now, assume it's handled globally or by the calling script.
    import os

    # Determine default archive folder
    if archive_folder is None:
        pic_folder = "My Pictures" if os.name == "nt" else "Pictures"
        default_base = Path(os.path.expanduser("~"), pic_folder, "midjourney")
        archive_path = default_base / "dimjournal"
    else:
        archive_path = Path(archive_folder)

    try:
        archive_path.mkdir(parents=True, exist_ok=True)
        _log.info(f"Data will be saved in: {archive_path.resolve()}")
    except OSError as e:
        _log.error(
            f"Could not create/access archive folder at "
            f"{archive_path.resolve()}: {e}",
            exc_info=True,
        )
        error_message = (  # noqa: E501
            f"Error: Could not create/access archive folder at "
            f"{archive_path.resolve()}.\nCheck permissions "
            "or specify another folder."
        )
        print(error_message)
        return

    options = webdriver.ChromeOptions()
    # Example options:
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    driver = None
    try:
        _log.info("Initializing WebDriver...")
        driver = webdriver.Chrome(use_subprocess=True, options=options)
        _log.info("WebDriver initialized.")

        api = MidjourneyAPI(driver=driver, archive_folder=archive_path)
        if not api.session_token:
            _log.error("Midjourney login failed. Check credentials/network.")
            print(
                "Login to Midjourney failed. Ensure manual login works and try again."
            )
            return
        if not api.user_id:
            _log.error("Failed to retrieve User ID. Archiving may be incomplete.")
            print("Could not retrieve User ID. Some features might be limited.")

        _log.info("Starting crawl for 'upscale' jobs.")
        upscale_crawler = MidjourneyJobCrawler(api, archive_path, job_type="upscale")
        upscale_crawler.crawl(limit=limit)
        _log.info("Finished crawl for 'upscale' jobs.")

        _log.info("Starting crawl for all job types.")
        all_jobs_crawler = MidjourneyJobCrawler(api, archive_path, job_type=None)
        all_jobs_crawler.crawl(limit=limit)
        _log.info("Finished crawl for all job types.")

        _log.info("Starting download of missing images.")
        downloader = MidjourneyDownloader(api, archive_path)
        downloader.download_missing()
        _log.info("Finished downloading missing images.")

    except KeyboardInterrupt:
        _log.warning("Process interrupted by user.")
        print("\nProcess interrupted by user.")
    except Exception as e:
        _log.critical(f"Critical error in download process: {str(e)}", exc_info=True)
        print(f"A critical error occurred: {str(e)}")
    finally:
        if driver:
            _log.info("Quitting WebDriver.")
            driver.quit()
        _log.info("Dimjournal process finished.")
