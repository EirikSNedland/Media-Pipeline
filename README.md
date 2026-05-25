# Media-Pipeline
A repo that combines multiple projects into one, and gives them a web interface

## Features
Small application that allows for manipulating files
* Unzip and extract spesified file type
* Bulk rip subbtitles from video files
* Bulk convert subtitle formats ass and sup to .srt, also works directly on .mkv files that uses .sup
* Bulk rename while keeping episode and season number. (Only rename one season at a time if default season variable is required)

## How to setup
* Change ```<local_download_folder>``` to local pc download folder or other folder serving similar purpose in docker-compose.yml
* Run ```docker compose up``` in terminal
* Webpage accessible through ```localhost:8051```
