import requests
import time
from pathlib import Path

### Mandatory Settings
url_template = lambda number: f"http://thedomain/static_url-{number}.ts"
starting_from_part_number = 1
CLIP_DURATION_IN_SECONDS = 2
MIN_FILE_SIZE_IN_BYTES = 150 * 1024
###

DOWNLOAD_FOLDER = "livestream_download"
Path(DOWNLOAD_FOLDER).mkdir(exist_ok=True)


def download_part(url):
    download_file_name = lambda name: f"{DOWNLOAD_FOLDER}/{name}"
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        name = url.split("/")[-1]
        filename = (download_file_name(name),)
        with open(
            filename,
            "wb",
        ) as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return filename


def download(starting_part_number):
    number = starting_part_number
    while True:
        filename = download_part(url_template(number))
        number += 1
        if Path(filename).stat().st_size() < MIN_FILE_SIZE_IN_BYTES:
            break
        time.sleep(CLIP_DURATION_IN_SECONDS)


if __name__ == "__main__":
    download(starting_from_part_number)
