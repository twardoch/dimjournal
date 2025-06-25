# import undetected_chromedriver as webdriver # Avoid direct import if using mocks
import datetime as dt
import json

import pytest

from dimjournal.dimjournal import Constants, get_date_ninety_days_prior

# Mocking Constants for testing if needed, or use the actual ones
# Constants.date_format = "%Y-%m-%d %H:%M:%S.%f"


def test_get_date_ninety_days_prior():
    """Test the get_date_ninety_days_prior function."""
    date_str = "2023-10-01 12:00:00.000000"
    # expected_date_str = "2023-07-03 12:00:00.000000"  # This was unused

    # Calculate expected date robustly for verification
    original_date = dt.datetime.strptime(date_str, Constants.date_format)
    expected_date_obj = original_date - dt.timedelta(days=90)
    calculated_expected_str = expected_date_obj.strftime(Constants.date_format)

    assert get_date_ninety_days_prior(date_str) == calculated_expected_str


def test_get_date_ninety_days_prior_leap_year():
    """Test get_date_ninety_days_prior function across a leap year."""
    # Date after Feb 29 in a leap year
    date_str = "2024-03-15 10:00:00.000000"  # 2024 is a leap year
    # Expected: 2024-03-15 minus 90 days = 2023-12-16
    original_date = dt.datetime.strptime(date_str, Constants.date_format)
    expected_date_obj = original_date - dt.timedelta(days=90)
    expected_date_str = expected_date_obj.strftime(Constants.date_format)

    assert get_date_ninety_days_prior(date_str) == expected_date_str


@pytest.fixture
def mock_driver(mocker):
    driver = mocker.MagicMock()
    mocker.patch(
        "dimjournal.dimjournal.WebDriverWait"
    )  # Mock to prevent actual waiting
    mocker.patch("dimjournal.dimjournal.EC")
    return driver


@pytest.fixture
def mock_api(mocker, mock_driver, tmp_path):
    mocker.patch("pickle.dump")  # Mock saving cookies
    mocker.patch("pickle.load", return_value=[])  # Mock loading cookies

    archive_dir = tmp_path / "archive"
    archive_dir.mkdir()

    from dimjournal.dimjournal import MidjourneyAPI  # Import for mocked context

    api = MidjourneyAPI(driver=mock_driver, archive_folder=archive_dir)
    return api


class TestMidjourneyAPI:
    def test_log_in_success(self, mock_api, mock_driver):
        mock_driver.get_cookie.return_value = {
            "name": Constants.session_token_cookie,
            "value": "test_token",
        }

        assert mock_api.log_in() is True
        mock_driver.get.assert_called_with(Constants.home_url)
        assert mock_api.session_token == "test_token"

    def test_log_in_failure_no_cookie(self, mock_api, mock_driver):
        mock_driver.get_cookie.return_value = None
        assert mock_api.log_in() is False

    def test_get_user_info_success_from_fetch(
        self, mock_api, mock_driver, mocker, tmp_path
    ):
        # Ensure user.json does not exist to force fetch
        user_json_path = tmp_path / "archive" / Constants.user_json
        if user_json_path.exists():
            user_json_path.unlink()

        mock_user_data = {"props": {"pageProps": {"user": {"id": "test_user_id"}}}}
        # Mock BeautifulSoup and script tag finding
        mock_soup = mocker.MagicMock()
        mock_script_tag = mocker.MagicMock()
        mock_script_tag.text = json.dumps(mock_user_data)
        mock_soup.find.return_value = mock_script_tag
        mocker.patch("dimjournal.dimjournal.BeautifulSoup", return_value=mock_soup)

        # Mock json.dump for saving user.json
        mocker.patch("json.dump")

        assert mock_api.get_user_info() is True
        assert mock_api.user_id == "test_user_id"
        mock_driver.get.assert_called_with(Constants.account_url)
        # Check if user.json was attempted to be written (content check is harder here)
        assert (tmp_path / "archive" / Constants.user_json).exists()

    def test_get_user_info_success_from_file(
        self, mock_api, mock_driver, mocker, tmp_path
    ):
        user_json_path = tmp_path / "archive" / Constants.user_json
        mock_user_data = {
            "props": {"pageProps": {"user": {"id": "test_user_id_from_file"}}}
        }
        with open(user_json_path, "w") as f:
            json.dump(mock_user_data, f)

        # We don't want fetch_user_info to be called
        mock_fetch = mocker.patch.object(mock_api, "fetch_user_info")

        assert mock_api.get_user_info() is True
        assert mock_api.user_id == "test_user_id_from_file"
        mock_fetch.assert_not_called()

    def test_request_recent_jobs_success(self, mock_api, mock_driver, mocker):
        mock_api.user_id = "test_user_id"
        mock_job_data = [{"id": "job1", "enqueue_time": "t1", "prompt": "p1"}]

        mock_soup = mocker.MagicMock()
        mock_pre_tag = mocker.MagicMock()
        mock_pre_tag.text = json.dumps(mock_job_data)
        mock_soup.find.return_value = mock_pre_tag
        mocker.patch("dimjournal.dimjournal.BeautifulSoup", return_value=mock_soup)

        jobs = mock_api.request_recent_jobs(page=1, amount=10)
        assert jobs == mock_job_data
        url_params = (
            "page=1&amount=10&orderBy=new&jobStatus=completed"
            "&userId=test_user_id&dedupe=true&refreshApi=0"
        )
        mock_driver.get.assert_called_with(f"{Constants.api_url}?{url_params}")

    def test_request_recent_jobs_no_jobs_found(self, mock_api, mock_driver, mocker):
        mock_api.user_id = "test_user_id"
        mock_response = [{"msg": "No jobs found."}]

        mock_soup = mocker.MagicMock()
        mock_pre_tag = mocker.MagicMock()
        mock_pre_tag.text = json.dumps(mock_response)
        mock_soup.find.return_value = mock_pre_tag
        mocker.patch("dimjournal.dimjournal.BeautifulSoup", return_value=mock_soup)

        jobs = mock_api.request_recent_jobs(page=1)
        assert jobs == []  # Expect empty list


@pytest.fixture
def mock_crawler(mocker, mock_api, tmp_path):  # Use mock_api fixture
    archive_dir = tmp_path / "crawler_archive"
    archive_dir.mkdir()

    from dimjournal.dimjournal import MidjourneyJobCrawler  # Local import for fixture

    crawler = MidjourneyJobCrawler(
        api=mock_api, archive_folder=archive_dir, job_type="upscale"
    )
    return crawler


class TestMidjourneyJobCrawler:
    def test_load_archive_data_file_exists(self, mock_crawler, tmp_path, mocker):
        archive_file = tmp_path / "crawler_archive" / "jobs_upscale.json"
        mock_data = [{"id": "job1", "prompt": "test"}]
        with open(archive_file, "w") as f:
            json.dump(mock_data, f)

        mock_crawler.load_archive_data()
        assert mock_crawler.archive_data == mock_data

    def test_load_archive_data_file_not_exists(self, mock_crawler):
        # Ensure file does not exist (should be handled by tmp_path if clean)
        mock_crawler.load_archive_data()
        assert mock_crawler.archive_data == []

    def test_load_archive_data_json_decode_error(self, mock_crawler, tmp_path, mocker):
        archive_file = tmp_path / "crawler_archive" / "jobs_upscale.json"
        with open(archive_file, "w") as f:
            f.write("this is not json")

        # Mock logging to check for error messages if needed
        # mock_log_error = mocker.patch('logging.Logger.error')

        mock_crawler.load_archive_data()
        assert mock_crawler.archive_data == []  # Should reset to empty
        # mock_log_error.assert_called_with(mocker.ANY, exc_info=True)

    def test_update_archive_data_new_entries(self, mock_crawler, tmp_path):
        mock_crawler.archive_data = [{"id": "job1"}]
        new_jobs = [{"id": "job2"}, {"id": "job3"}]

        assert mock_crawler.update_archive_data(new_jobs) is True
        assert len(mock_crawler.archive_data) == 3
        assert mock_crawler.archive_data[-1]["id"] == "job3"

        archive_file = tmp_path / "crawler_archive" / "jobs_upscale.json"
        with open(archive_file, "r") as f:
            saved_data = json.load(f)
        assert len(saved_data) == 3

    def test_update_archive_data_no_new_entries(self, mock_crawler):
        mock_crawler.archive_data = [{"id": "job1"}]
        existing_jobs = [{"id": "job1"}]

        assert mock_crawler.update_archive_data(existing_jobs) is False
        assert len(mock_crawler.archive_data) == 1

    def test_crawl_success_gathers_jobs(self, mock_crawler, mocker):
        mock_api_request = mocker.patch.object(mock_crawler.api, "request_recent_jobs")
        mock_api_request.side_effect = [
            [
                {"id": "j1", "enqueue_time": "t1", "prompt": "p1"},
                {"id": "j2", "enqueue_time": "t2", "prompt": "p2"},
            ],
            [{"id": "j3", "enqueue_time": "t3", "prompt": "p3"}],
            [],  # Empty list simulates end of jobs
        ]

        mock_crawler.crawl(limit=5)

        assert len(mock_crawler.archive_data) == 3
        assert mock_crawler.archive_data[0]["id"] == "j1"
        assert mock_crawler.archive_data[2]["id"] == "j3"
        assert mock_api_request.call_count == 3

    def test_crawl_stops_when_no_new_data(self, mock_crawler, mocker):
        mock_api_request = mocker.patch.object(mock_crawler.api, "request_recent_jobs")
        jobs_page1 = [{"id": "j1", "enqueue_time": "t1", "prompt": "p1"}]
        mock_api_request.side_effect = [jobs_page1, jobs_page1]  # Same data twice

        mock_crawler.crawl(limit=5)

        assert len(mock_crawler.archive_data) == 1
        assert mock_api_request.call_count == 2


@pytest.fixture
def mock_downloader(mocker, mock_api, tmp_path):
    archive_dir = tmp_path / "downloader_archive"
    archive_dir.mkdir()

    dummy_jobs_file = archive_dir / "jobs_upscale.json"
    initial_jobs = [
        {
            "id": "dl1",
            "enqueue_time": "2023-01-01 10:00:00.000000",
            "prompt": "prompt1",
            "image_paths": ["http://example.com/img1.png"],
            "username": "user1",
            "full_command": "/imagine prompt1",
        },
        {
            "id": "dl2",
            "enqueue_time": "2023-01-02 11:00:00.000000",
            "prompt": "prompt2",
            "image_paths": ["http://example.com/img2.jpg"],
            "username": "user1",
            "full_command": "/imagine prompt2",
            "arch": True,
            "arch_image_path": "2023/01/img2.jpg",
        },
    ]
    with open(dummy_jobs_file, "w") as f:
        json.dump(initial_jobs, f)

    from dimjournal.dimjournal import MidjourneyDownloader  # Local import

    downloader = MidjourneyDownloader(api=mock_api, archive_folder=archive_dir)
    return downloader


class TestMidjourneyDownloader:
    def test_read_jobs_success(self, mock_downloader):
        assert len(mock_downloader.jobs_upscale) == 2
        assert mock_downloader.jobs_upscale[0]["id"] == "dl1"

    def test_read_jobs_file_not_found(self, mocker, mock_api, tmp_path):
        non_existent_archive_dir = tmp_path / "non_existent_archive"
        non_existent_archive_dir.mkdir()

        from dimjournal.dimjournal import MidjourneyDownloader  # Local import

        downloader = MidjourneyDownloader(
            api=mock_api, archive_folder=non_existent_archive_dir
        )
        assert downloader.jobs_upscale == []

    def test_create_folders(self, mock_downloader, tmp_path):
        downloader_archive_path = tmp_path / "downloader_archive"
        dt_obj = dt.datetime(2023, 5, 15)
        path_month = mock_downloader.create_folders(dt_obj)

        expected_path = downloader_archive_path / "2023" / "05"
        assert path_month == expected_path
        assert expected_path.is_dir()

    def test_fetch_and_write_image_png_success(self, mock_downloader, mocker, tmp_path):
        mock_fetch_image = mocker.patch.object(mock_downloader, "fetch_image")
        # Simulate fetching a PNG
        raw_image_data = b"fakedata_png"  # Minimal bytes for open
        mock_fetch_image.return_value = (raw_image_data, "png")

        # Mock np.array, Image.open, pymtpng.encode_png
        mocker.patch("numpy.array")
        mock_image_open = mocker.patch("PIL.Image.open")
        mock_pymtpng_encode = mocker.patch("pymtpng.encode_png")

        image_url = "http://example.com/new_image.png"
        image_path = tmp_path / "downloader_archive" / "new_image.png"
        info = {"Title": "Test PNG"}

        assert (
            mock_downloader.fetch_and_write_image(image_url, image_path, info) is True
        )
        mock_fetch_image.assert_called_once_with(image_url)
        mock_image_open.assert_called_once_with(mocker.ANY)  # io.BytesIO object
        mock_pymtpng_encode.assert_called_once()
        assert image_path.exists()  # Check if open was called in write mode
        # To truly check content, you'd let pymtpng write and then read, but that's more involved.

    def test_fetch_and_write_image_non_png(self, mock_downloader, mocker, tmp_path):
        mock_fetch_image = mocker.patch.object(mock_downloader, "fetch_image")
        raw_image_data = b"fakedata_jpg"
        mock_fetch_image.return_value = (raw_image_data, "jpeg")

        image_url = "http://example.com/new_image.jpg"
        image_path = tmp_path / "downloader_archive" / "new_image.jpg"
        info = {}  # Info not used for non-PNG usually

        assert (
            mock_downloader.fetch_and_write_image(image_url, image_path, info) is True
        )
        mock_fetch_image.assert_called_once_with(image_url)
        assert image_path.exists()
        with open(image_path, "rb") as f:
            assert f.read() == raw_image_data

    def test_fetch_and_write_image_already_exists(
        self, mock_downloader, mocker, tmp_path
    ):
        image_path = tmp_path / "downloader_archive" / "existing.png"
        with open(image_path, "w") as f:
            f.write("exists")  # Create dummy file

        mock_fetch_image = mocker.patch.object(mock_downloader, "fetch_image")
        assert mock_downloader.fetch_and_write_image("url", image_path, {}) is False
        mock_fetch_image.assert_not_called()

    def test_download_missing_downloads_one_image(
        self, mock_downloader, mocker, tmp_path
    ):
        # jobs_upscale has one downloadable item (dl_job1) and one archived (dl_job2)

        # Mock fetch_and_write_image to simulate successful download for the first job
        mock_faw_image = mocker.patch.object(mock_downloader, "fetch_and_write_image")

        # Make it return True only for the first call (non-archived item)
        # This logic is a bit tricky. Let's simplify: assume it's called for the non-archived one.
        # We'll check that it was called for the correct URL.

        # Path for dl1 (non-archived job)
        archive_base = tmp_path / "downloader_archive"
        year_dir = archive_base / "2023"
        month_dir = year_dir / "01"
        # Break long string
        img_fn_part1 = "20230101-1000"
        img_fn_part2 = "_prompt1_dl1.png"  # noqa: E501
        expected_image_filename = img_fn_part1 + img_fn_part2
        expected_image_path = month_dir / expected_image_filename
        expected_path_str = "2023/01/" + expected_image_filename

        def side_effect_faw(img_url, img_path, info_dict):  # Renamed for clarity
            if (
                img_url == "http://example.com/img1.png"
                and img_path == expected_image_path
            ):
                img_path.parent.mkdir(parents=True, exist_ok=True)
                with open(img_path, "wb") as f:
                    f.write(b"downloaded_content")
                return True
            return False

        mock_save_jobs = mocker.patch.object(
            mock_downloader, "save_jobs"
        )  # Patch before calling
        mock_faw_image.side_effect = side_effect_faw

        mock_downloader.download_missing()

        args_list = mock_faw_image.call_args_list
        assert len(args_list) == 1  # Only dl1 should be processed

        called_args = args_list[0][0]
        assert called_args[0] == "http://example.com/img1.png"  # url
        assert called_args[1] == expected_image_path  # path
        assert called_args[2]["Title"] == "prompt1"  # info check

        # Verify job metadata update for dl1
        job_dl1 = mock_downloader.jobs_upscale[0]
        assert job_dl1["arch"] is True
        # Break long assertion
        arch_path = job_dl1["arch_image_path"]
        assert arch_path == expected_path_str  # noqa: E501

        # Verify dl2 (already archived) was not touched further by this download call
        assert mock_downloader.jobs_upscale[1]["id"] == "dl2"
        assert mock_downloader.jobs_upscale[1]["arch"] is True

        mock_save_jobs.assert_called_once()
