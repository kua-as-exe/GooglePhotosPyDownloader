# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib ipywidgets tqdm requests
import pickle
import os
import requests # pip install requests

from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

from tqdm import tqdm

def Create_Service(client_secret_file, api_name, api_version, *scopes):
    #print(client_secret_file, api_name, api_version, scopes, sep='-')
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    #print(SCOPES)

    cred = None

    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'
    # print(pickle_file)

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()
            #cred = flow.run_console()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred, static_discovery=False)
        # print(service)
        print(API_SERVICE_NAME, 'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect. ')
        print(e)
        return "Noup"
    

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'photoslibrary'
API_VERSION = 'v1'
SCOPES = ['https://www.googleapis.com/auth/photoslibrary']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

myAblums = service.albums().list().execute().get('albums')
print("")
print("Select an album: ")
index = 1;
for album in myAblums:
    print(f' {index}) "{album["title"]}" - {album["mediaItemsCount"]} fotos')
    index = index +1

index = int(input("Album number (eg: 3):"))-1
album = myAblums[index]

print()
print(f'Selected album: {album.get("title")} ({album.get("mediaItemsCount")} elements)')
print()

def createDirIfNotExists(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path

base = input("Enter base location (default: current directory):\n")
albumPath = os.path.join(base,'Google Photos', album["title"])
print(f'Path: "{albumPath}"')
createDirIfNotExists(albumPath)

pageSize = 100
pageToken = ""
items = []

while( len(items) < int(album["mediaItemsCount"]) ):
    albumData = service.mediaItems().search(body={'albumId': album['id'], 'pageSize': pageSize, 'pageToken': pageToken}).execute()
    media_files = albumData["mediaItems"]
    media_files = list(map( lambda x: {
        'filename': x['filename'],
        'baseUrl': x['baseUrl']
    }, media_files))
    items += media_files
    pageToken = albumData.get("nextPageToken", "")

#print(items[:10])
print(f'{len(items)} items loaded')

# https://stackoverflow.com/a/3207973
def dirContent(mypath: str):
    from os import listdir
    from os.path import isfile, join
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    return files

def download_file(url:str, destination_folder:str, file_name:str):
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(destination_folder, file_name), 'wb') as f:
            f.write(response.content)
            f.close()


alreadyDownloaded = len(dirContent(albumPath))
print(f'Already downloaded: {alreadyDownloaded}')

pbar=tqdm(total=len(items), initial=alreadyDownloaded)
i=0
try:
    for i in range(alreadyDownloaded, len(items)):
        media_file = items[i]
        file_name = media_file['filename']
        download_url = media_file['baseUrl'] + '=d'
        download_file(download_url, albumPath, file_name)
        pbar.update(1)
        
except KeyboardInterrupt:
    print(f"Process stopped, images downloaded: {len(dirContent(albumPath))}")
