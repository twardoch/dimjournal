# dimjournal

dimjournal is a Python utility for automatically downloading upscaled images from Midjourney into a local archive (folder tree). 

Note: the terms of use of Midjourney disallow any automation!

dimjournal uses the Selenium WebDriver to log into the Midjourney website, fetch user data, and download job information and images. The files are stored a folder of your choice.

## Installation

```
python3 -m pip install git+https://github.com/twardoch/dimjournal
```

## Usage

### Command Line Interface (CLI)

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

