import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """

    try:
        service = create_drive_service()

        parent = "BrazilianCharts"
        parent_folder = get_folder(name=parent, service=service)
        parent_id = parent_folder['id']

        for item in iter_folder_files(parent_id, service):
            print(u'{0} ({1})'.format(item['name'], item['id']))

    except HttpError as error:
        print(f'An error occurred: {error}')


def create_drive_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)


def get_folder(name: str, service):
    result = service.files().list(
        q=f"trashed=false and name='{name}'",
    ).execute()
    fs = result.get('files', [])
    if len(fs) != 1:
        raise ValueError("Google API sucks")
    return fs[0]


def iter_folder_files(folder_parent_id: str, service):
    done = False
    next_page_token = None
    while not done:
        # Call the Drive v3 API
        results = service.files().list(
            q=f"trashed=false and parents in '{folder_parent_id}'",
            pageSize=10,
            fields="nextPageToken, files(id, name)",
            pageToken=next_page_token,
        ).execute()
        items = results.get('files', [])
        next_page_token = results.get("nextPageToken")
        if next_page_token is None:
            done = True
 
        if not items:
            print('No files found.')
            return None
        for item in items:
            yield item
 

if __name__ == '__main__':
    main()
