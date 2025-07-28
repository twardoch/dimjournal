# this_file: tests/test_dimjournal.py
"""
Comprehensive test suite for dimjournal package.
"""
import pytest
import json
import pickle
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import datetime as dt
from tempfile import TemporaryDirectory

from dimjournal.dimjournal import (
    get_date_ninety_days_prior,
    Constants,
    MidjourneyAPI,
    MidjourneyJobCrawler,
    MidjourneyDownloader,
    download
)


class TestUtilityFunctions:
    """Test utility functions."""

    def test_get_date_ninety_days_prior(self):
        """Test get_date_ninety_days_prior function."""
        # Test with a known date
        test_date = "2023-12-01 12:00:00.000000"
        expected = "2023-09-02 12:00:00.000000"
        result = get_date_ninety_days_prior(test_date)
        assert result == expected

    def test_get_date_ninety_days_prior_leap_year(self):
        """Test get_date_ninety_days_prior with leap year."""
        test_date = "2024-03-01 12:00:00.000000"
        expected = "2023-12-01 12:00:00.000000"
        result = get_date_ninety_days_prior(test_date)
        assert result == expected


class TestConstants:
    """Test Constants class."""

    def test_constants_values(self):
        """Test that constants have expected values."""
        assert Constants.date_format == "%Y-%m-%d %H:%M:%S.%f"
        assert Constants.home_url == "https://www.midjourney.com/home/"
        assert Constants.app_url == "https://www.midjourney.com/app/"
        assert Constants.account_url == "https://www.midjourney.com/account/"
        assert Constants.api_url == "https://www.midjourney.com/api/app/recent-jobs/"
        assert Constants.session_token_cookie == "__Secure-next-auth.session-token"
        assert Constants.app_element_id == "app-root"
        assert Constants.account_element_id == "__NEXT_DATA__"
        assert Constants.job_details == ["id", "enqueue_time", "prompt"]


class TestMidjourneyAPI:
    """Test MidjourneyAPI class."""

    @pytest.fixture
    def mock_driver(self):
        """Create a mock Chrome driver."""
        driver = Mock()
        driver.get_cookies.return_value = []
        driver.add_cookie = Mock()
        driver.get = Mock()
        driver.find_element = Mock()
        driver.execute_script = Mock()
        return driver

    @pytest.fixture
    def temp_archive(self):
        """Create a temporary archive directory."""
        with TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @patch('dimjournal.dimjournal.MidjourneyAPI.log_in')
    @patch('dimjournal.dimjournal.MidjourneyAPI.get_user_info')
    def test_init(self, mock_get_user_info, mock_log_in, mock_driver, temp_archive):
        """Test MidjourneyAPI initialization."""
        api = MidjourneyAPI(mock_driver, temp_archive)
        assert api.archive_folder == temp_archive
        assert api.driver == mock_driver
        mock_log_in.assert_called_once()
        mock_get_user_info.assert_called_once()

    @patch('dimjournal.dimjournal.MidjourneyAPI.log_in')
    @patch('dimjournal.dimjournal.MidjourneyAPI.get_user_info')
    def test_load_cookies_file_exists(self, mock_get_user_info, mock_log_in, mock_driver, temp_archive):
        """Test loading cookies when file exists."""
        # Create a mock cookies file
        cookies_path = temp_archive / Constants.cookies_pkl
        test_cookies = [{'name': 'test', 'value': 'value'}]
        
        with open(cookies_path, 'wb') as f:
            pickle.dump(test_cookies, f)
        
        api = MidjourneyAPI(mock_driver, temp_archive)
        api.load_cookies()
        
        mock_driver.add_cookie.assert_called_once_with(test_cookies[0])

    @patch('dimjournal.dimjournal.MidjourneyAPI.log_in')
    @patch('dimjournal.dimjournal.MidjourneyAPI.get_user_info')
    def test_load_cookies_file_not_exists(self, mock_get_user_info, mock_log_in, mock_driver, temp_archive):
        """Test loading cookies when file doesn't exist."""
        api = MidjourneyAPI(mock_driver, temp_archive)
        api.load_cookies()  # Should not raise exception
        mock_driver.add_cookie.assert_not_called()

    @patch('dimjournal.dimjournal.MidjourneyAPI.log_in')
    @patch('dimjournal.dimjournal.MidjourneyAPI.get_user_info')
    def test_save_cookies(self, mock_get_user_info, mock_log_in, mock_driver, temp_archive):
        """Test saving cookies."""
        test_cookies = [{'name': 'test', 'value': 'value'}]
        mock_driver.get_cookies.return_value = test_cookies
        
        api = MidjourneyAPI(mock_driver, temp_archive)
        api.save_cookies()
        
        # Verify cookies were saved
        cookies_path = temp_archive / Constants.cookies_pkl
        assert cookies_path.exists()
        
        with open(cookies_path, 'rb') as f:
            saved_cookies = pickle.load(f)
        
        assert saved_cookies == test_cookies


class TestMidjourneyJobCrawler:
    """Test MidjourneyJobCrawler class."""

    @pytest.fixture
    def mock_api(self):
        """Create a mock MidjourneyAPI."""
        api = Mock()
        api.request_recent_jobs = Mock()
        return api

    @pytest.fixture
    def temp_archive(self):
        """Create a temporary archive directory."""
        with TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_init(self, mock_api, temp_archive):
        """Test MidjourneyJobCrawler initialization."""
        crawler = MidjourneyJobCrawler(mock_api, temp_archive, "upscale")
        assert crawler.api == mock_api
        assert crawler.archive_folder == temp_archive
        assert crawler.job_type == "upscale"

    def test_load_archive_data_file_exists(self, mock_api, temp_archive):
        """Test loading archive data when file exists."""
        # Create test data file
        jobs_file = temp_archive / "jobs_upscale.json"
        test_data = {"jobs": [{"id": "test1", "prompt": "test prompt"}]}
        
        with open(jobs_file, 'w') as f:
            json.dump(test_data, f)
        
        crawler = MidjourneyJobCrawler(mock_api, temp_archive, "upscale")
        data = crawler.load_archive_data()
        
        assert data == test_data

    def test_load_archive_data_file_not_exists(self, mock_api, temp_archive):
        """Test loading archive data when file doesn't exist."""
        crawler = MidjourneyJobCrawler(mock_api, temp_archive, "upscale")
        data = crawler.load_archive_data()
        
        assert data == {"jobs": []}

    def test_update_archive_data(self, mock_api, temp_archive):
        """Test updating archive data."""
        crawler = MidjourneyJobCrawler(mock_api, temp_archive, "upscale")
        
        # Create initial data
        initial_data = {"jobs": [{"id": "test1", "prompt": "test1"}]}
        new_jobs = [{"id": "test2", "prompt": "test2"}]
        
        crawler.archive_data = initial_data
        crawler.update_archive_data(new_jobs)
        
        # Verify data was updated
        assert len(crawler.archive_data["jobs"]) == 2
        assert crawler.archive_data["jobs"][-1]["id"] == "test2"

    def test_crawl_with_limit(self, mock_api, temp_archive):
        """Test crawling with limit."""
        mock_api.request_recent_jobs.return_value = [
            {"id": "job1", "prompt": "test1"},
            {"id": "job2", "prompt": "test2"}
        ]
        
        crawler = MidjourneyJobCrawler(mock_api, temp_archive, "upscale")
        crawler.crawl(limit=1)
        
        # Should only make one API call due to limit
        assert mock_api.request_recent_jobs.call_count == 1


class TestMidjourneyDownloader:
    """Test MidjourneyDownloader class."""

    @pytest.fixture
    def mock_api(self):
        """Create a mock MidjourneyAPI."""
        api = Mock()
        api.fetch_image = Mock()
        api.archive_folder = Path("/tmp/test")
        return api

    @pytest.fixture
    def temp_archive(self):
        """Create a temporary archive directory."""
        with TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_init(self, mock_api, temp_archive):
        """Test MidjourneyDownloader initialization."""
        downloader = MidjourneyDownloader(mock_api, temp_archive)
        assert downloader.api == mock_api
        assert downloader.archive_folder == temp_archive

    def test_create_folders(self, mock_api, temp_archive):
        """Test folder creation."""
        downloader = MidjourneyDownloader(mock_api, temp_archive)
        
        # Test with a specific date
        test_date = dt.datetime(2023, 12, 1, 12, 0, 0)
        folder_path = downloader.create_folders(test_date)
        
        expected_path = temp_archive / "2023" / "12"
        assert folder_path == expected_path
        assert folder_path.exists()

    def test_generate_image_path(self, mock_api, temp_archive):
        """Test image path generation."""
        downloader = MidjourneyDownloader(mock_api, temp_archive)
        
        # Test job data
        job_data = {
            "id": "test-job-id-123",
            "enqueue_time": "2023-12-01 12:00:00.000000",
            "prompt": "A beautiful landscape with mountains"
        }
        
        image_path = downloader.generate_image_path(job_data)
        
        # Check path components
        assert "2023" in str(image_path)
        assert "12" in str(image_path)
        assert "20231201-1200" in str(image_path)
        assert "beautiful-landscape-with-mountains" in str(image_path)
        assert "test" in str(image_path)  # First 4 chars of job ID
        assert image_path.suffix == ".png"

    @patch('dimjournal.dimjournal.MidjourneyDownloader.fetch_and_write_image')
    def test_download_missing_images(self, mock_fetch_write, mock_api, temp_archive):
        """Test downloading missing images."""
        # Setup mock data
        jobs_data = {
            "jobs": [
                {
                    "id": "job1",
                    "enqueue_time": "2023-12-01 12:00:00.000000",
                    "prompt": "test prompt 1",
                    "image_paths": ["http://example.com/image1.png"]
                },
                {
                    "id": "job2",
                    "enqueue_time": "2023-12-01 12:00:00.000000",
                    "prompt": "test prompt 2",
                    "image_paths": ["http://example.com/image2.png"]
                }
            ]
        }
        
        # Create jobs file
        jobs_file = temp_archive / Constants.jobs_upscaled_json
        with open(jobs_file, 'w') as f:
            json.dump(jobs_data, f)
        
        downloader = MidjourneyDownloader(mock_api, temp_archive)
        downloader.download_missing()
        
        # Should attempt to download both images
        assert mock_fetch_write.call_count == 2


class TestDownloadFunction:
    """Test the main download function."""

    @patch('dimjournal.dimjournal.webdriver.Chrome')
    @patch('dimjournal.dimjournal.MidjourneyAPI')
    @patch('dimjournal.dimjournal.MidjourneyJobCrawler')
    @patch('dimjournal.dimjournal.MidjourneyDownloader')
    def test_download_function_success(self, mock_downloader_class, mock_crawler_class, 
                                     mock_api_class, mock_driver_class, tmp_path):
        """Test successful download function execution."""
        # Setup mocks
        mock_driver = Mock()
        mock_driver_class.return_value = mock_driver
        
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        
        mock_crawler = Mock()
        mock_crawler_class.return_value = mock_crawler
        
        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader
        
        # Call download function
        result = download(archive_folder=tmp_path, limit=5)
        
        # Verify mocks were called
        mock_driver_class.assert_called_once()
        mock_api_class.assert_called_once_with(mock_driver, tmp_path)
        assert mock_crawler_class.call_count == 2  # Called for upscale and all jobs
        mock_downloader_class.assert_called_once_with(mock_api, tmp_path)
        
        # Verify driver was quit
        mock_driver.quit.assert_called_once()

    @patch('dimjournal.dimjournal.webdriver.Chrome')
    def test_download_function_with_exception(self, mock_driver_class, tmp_path):
        """Test download function with exception handling."""
        # Setup driver mock
        mock_driver = Mock()
        mock_driver_class.return_value = mock_driver
        
        # Make API initialization raise an exception
        with patch('dimjournal.dimjournal.MidjourneyAPI') as mock_api_class:
            mock_api_class.side_effect = Exception("Test exception")
            
            # Should not raise exception, but should still quit driver
            download(archive_folder=tmp_path)
            
            # Verify driver was quit even with exception
            mock_driver.quit.assert_called_once()


class TestIntegration:
    """Integration tests."""

    def test_package_imports(self):
        """Test that package imports work correctly."""
        from dimjournal import download
        from dimjournal import __version__
        
        # Should be able to import main functions
        assert callable(download)
        assert isinstance(__version__, str)

    def test_cli_entry_point(self):
        """Test CLI entry point exists."""
        from dimjournal.__main__ import cli
        assert callable(cli)


# Test fixtures for common test data
@pytest.fixture
def sample_job_data():
    """Sample job data for tests."""
    return {
        "id": "test-job-id-123456",
        "enqueue_time": "2023-12-01 12:00:00.000000",
        "prompt": "A beautiful landscape with mountains and rivers",
        "image_paths": ["http://example.com/test-image.png"]
    }


@pytest.fixture
def sample_jobs_list():
    """Sample jobs list for tests."""
    return [
        {
            "id": "job1",
            "enqueue_time": "2023-12-01 12:00:00.000000",
            "prompt": "test prompt 1",
            "image_paths": ["http://example.com/image1.png"]
        },
        {
            "id": "job2", 
            "enqueue_time": "2023-12-01 13:00:00.000000",
            "prompt": "test prompt 2",
            "image_paths": ["http://example.com/image2.png"]
        }
    ]


# Additional utility tests
class TestErrorHandling:
    """Test error handling scenarios."""

    def test_invalid_date_format(self):
        """Test handling of invalid date format."""
        with pytest.raises(ValueError):
            get_date_ninety_days_prior("invalid-date")

    def test_missing_archive_folder(self):
        """Test handling of missing archive folder."""
        with patch('dimjournal.dimjournal.webdriver.Chrome') as mock_driver_class:
            mock_driver = Mock()
            mock_driver_class.return_value = mock_driver
            
            # Should create the folder if it doesn't exist
            non_existent_path = Path("/tmp/non-existent-folder")
            
            with patch('dimjournal.dimjournal.MidjourneyAPI') as mock_api_class:
                mock_api = Mock()
                mock_api_class.return_value = mock_api
                
                # Should not raise exception
                download(archive_folder=non_existent_path)
                
                mock_driver.quit.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])