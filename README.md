# Python script to download Google Photos albums

## Features:

- Interactive CLI to choose album and download location
- Resume download if process was stopped 

## Example
<img src="https://i.imgur.com/7F5BFgz.png"/>

## Usage and instalation

Setup a Google Cloud Project with OAuth and Google Photos API as the example in this video: ![Jie Jenn - Set up your first Google Cloud Project and download Client File (JSON file)](https://www.youtube.com/watch?v=6bzzpda63H0) and download the JSON file as `credentials.json` on this directory

```sh
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib ipywidgets tqdm requests
python main.py
```
