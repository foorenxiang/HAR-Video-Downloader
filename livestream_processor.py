from pathlib import Path
import subprocess

TS_FILENAME = "./outputs/livestream.ts"
MP4_FILENAME = TS_FILENAME.replace(".ts", ".mp4")

video_parts = tuple(sorted(Path("livestream_download").glob("*.ts")))

with open(TS_FILENAME, "wb") as wfp:
    for video_part in video_parts:
        with open(video_part, "rb") as rfp:
            wfp.write(rfp.read())
subprocess.run(["ffmpeg", "-i", TS_FILENAME, MP4_FILENAME])
