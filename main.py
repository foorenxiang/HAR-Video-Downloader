from pathlib import Path
from typing import List
import requests
import os
import subprocess
import time

from requests.models import HTTPError

OUTPUT_DIR = "outputs"
DOWNLOADED_VIDEO_EXTENSION = ".ts"
CONVERTED_FILE_EXTENSION = ".mp4"


def get_har_filepaths() -> Path:
    return Path("inputs").glob("*.har")


def get_har_filename(har_file: Path) -> str:
    return har_file.name


def extract_url(line: str) -> str:
    components = line.split('"')

    for component in components:
        if "?" in component:
            component = component.split("?")[0]
        if component.endswith(DOWNLOADED_VIDEO_EXTENSION):
            return component


def make_output_directory(har_filename: str) -> Path:
    output_dir_parent = Path(OUTPUT_DIR)
    output_dir_parent.mkdir(exist_ok=True)
    output_dir = output_dir_parent / har_filename
    output_dir.mkdir(exist_ok=True)
    return output_dir


def download_file(url: str, download_directory: Path) -> str:
    if not url:
        return
    local_filename = url.split("/")[-1]
    downloading_path = download_directory / f"{local_filename}.download"
    downloaded_path = download_directory / local_filename
    if downloaded_path.exists():
        return local_filename

    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(
                downloading_path,
                "wb",
            ) as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        os.rename(downloading_path, downloaded_path)
    except requests.exceptions.MissingSchema:
        pass

    return local_filename


def download_urls(urls: list, download_directory: Path) -> None:
    for url in urls:
        download_file(url, download_directory)


def download_videos(list_of_har_files) -> None:
    for har_file in list_of_har_files:
        har_filename = get_har_filename(har_file)
        print(f"Downloading {har_filename}")
        with open(har_file, "r") as fp:
            data = fp.readlines()
        video_urls = [
            extract_url(line) for line in data if DOWNLOADED_VIDEO_EXTENSION in line
        ]
        output_dir = make_output_directory(har_filename)
        download_urls(video_urls, output_dir)
    print("Downloads complete")


def list_video_parts(video_path: Path) -> List:
    video_parts = [
        str(ts_path) for ts_path in video_path.glob(f"*{DOWNLOADED_VIDEO_EXTENSION}")
    ]
    video_parts.sort()
    return video_parts


def combine_videos() -> None:
    print("Combining videos")
    video_file_paths = [
        path
        for path in Path(OUTPUT_DIR).glob("*")
        if path.is_dir and path.suffix == ".har"
    ]
    for video_path in video_file_paths:
        video_parts = list_video_parts(video_path)
        output_file = (
            video_path.parent / f"{video_path.stem}{DOWNLOADED_VIDEO_EXTENSION}"
        )
        output_file.touch()
        with open(output_file, "wb") as wfp:
            for video_part in video_parts:
                with open(video_part, "rb") as rfp:
                    wfp.write(rfp.read())


def convert_combined_videos_to_mp4() -> None:
    combined_videos = list(Path(OUTPUT_DIR).glob(f"*{DOWNLOADED_VIDEO_EXTENSION}"))
    output_videos = [
        (video.parent / f"{video.stem}{CONVERTED_FILE_EXTENSION}")
        for video in combined_videos
    ]
    print(combined_videos)
    print(output_videos)
    for input_video, output_video in zip(combined_videos, output_videos):
        print(f"Converting {output_video}")
        subprocess.run(["ffmpeg", "-i", str(input_video), str(output_video)])


if __name__ == "__main__":
    list_of_har_files = get_har_filepaths()
    download_videos(list_of_har_files)
    combine_videos()
    convert_combined_videos_to_mp4()
