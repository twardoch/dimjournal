# Dimjournal

Dimjournal is a Midjourney backup tool. It automatically downloads the metadata archive and the upscaled images from Midjourney into a local archive (folder tree). It also embeds some basic metadata (like the prompt) into the PNG files. 

_Note: the terms of use of Midjourney disallow any automation._

Dimjournal is a Python tool uses the Selenium WebDriver to log into the Midjourney website, fetch user data, and download job information and images. 

## Changelog

- v1.0.8: Fixes
- v1.0.3: Tested on macOS in July 2023

## Installation

Stable version:

```
pip install dimjournal
```

Development version:

```
python3 -m pip install git+https://github.com/twardoch/dimjournal
```

## Usage

### Command Line Interface (CLI)

In Terminal, run:

```bash
dimjournal
```

Dimjournal will open a browser where you need to log into MidJourney. The tool will create the backup folder, which by default is the `midjourney/dimjournal` subfolder inside your `Pictures`/`My Pictures` folder. It will operate the browser, download all metadata (up to 2,500 last upscale jobs, and up to 2,500 jobs), and save it in JSON files in the backup folder. Then it will use the browser to download all upscales that are not in the backup folder. If you run the tool again, it will only download new metadata, and new images. 

To specify a different backup folder, use: 

```bash
python3 -m dimjournal --archive_folder /path/to/your/archive/folder
```

### Python

You can also use Dimjournal in your Python scripts. Here is an example of how to import and use the `download` function:

```python
from dimjournal import download

# Specify the directory where you want to store the data
archive_folder = "/path/to/your/archive/folder"

# Download the data
download(archive_folder)
```

## License

- Licensed under the [Apache-2.0 License](./LICENSE.txt)
- Written with assistance from ChatGPT

