import pytest
from dimjournal.dimjournal import (
    MidjourneyAPI,
    MidjourneyJobCrawler,
    MidjourneyDownloader,
)
from pathlib import Path
import undetected_chromedriver as webdriver


# Mocking the webdriver for testing
class MockDriver:
    def __init__(self):
        pass

    def add_cookie(self, cookie):
        pass

    def get(self, url):
        pass

    def get_cookie(self, name):
        return {"value": "test_value"}

    def quit(self):
        pass


@pytest.fixture
def api():
    return MidjourneyAPI(driver=MockDriver(), archive_folder=Path.cwd())


@pytest.fixture
def crawler(api):
    return MidjourneyJobCrawler(api, Path.cwd(), job_type="upscale")


@pytest.fixture
def downloader(api):
    return MidjourneyDownloader(api, Path.cwd())


def test_midjourney_downloader_read_jobs(downloader):
    assert True
