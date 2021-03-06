# https://stackoverflow.com/questions/52591553/how-to-use-ffmpeg-with-gpu-support-on-macos

import requests
import time
from pathlib import Path
import subprocess

### Mandatory Settings
url_template = lambda number: f"http://thedomain/static_url-{number}.ts"
starting_from_part_number = 1
CLIP_DURATION_IN_SECONDS = 2
MIN_FILE_SIZE_IN_BYTES = 150 * 1024
TS_FILENAME = "./outputs/livestream.ts"
CONVERSION_BITRATE = "6000K"
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


def get_mp4_filename():
    MP4_FILENAME = TS_FILENAME.replace(".ts", ".mp4")
    return MP4_FILENAME


def get_ts_parts():
    video_parts = tuple(sorted(Path("livestream_download").glob("*.ts")))
    return video_parts


def convert_ts_to_mp4():
    MP4_FILENAME = get_mp4_filename()
    video_parts = get_ts_parts()
    with open(TS_FILENAME, "wb") as wfp:
        for video_part in video_parts:
            with open(video_part, "rb") as rfp:
                wfp.write(rfp.read())
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            TS_FILENAME,
            "-c:v h264_videotoolbox",
            f"-b:v {CONVERSION_BITRATE}",
            MP4_FILENAME,
        ]
    )


convert_ts_to_mp4()
if __name__ == "__main__":
    download(starting_from_part_number)
    convert_ts_to_mp4()
