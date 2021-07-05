# HAR video downloader

## Downloading videos split up into many xhr requests

Download strategy opts to redownload filtered xhr uris found in the HAR file rather than directly using captured responses as not all initial requests may be successful

### Installation

1. cd to project root
2. python3 -m venv venv
3. source venv/bin/activate
4. pip3 install requirements.txt

### Instructions

1. Open Chrome devtools and select network tab
2. Refresh page
3. Wait for video to finish playing
4. Save all as HAR (HTTP archive format)
5. Place HAR file(s) into 'inputs' folder of project
6. Run the script and wait for videos in 'outputs' folder
