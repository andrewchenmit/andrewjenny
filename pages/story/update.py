from __future__ import print_function
import json
import pickle
import os.path
import re
import urllib.request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from PIL import Image

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1FBHVusfenvRbUVBIZGpBo4btaG1ROfEEuO5PJ8jYrRI'
EVENT_RANGE = 'Story!A2:F'
CATEGORIES_RANGE = 'Categories!A2:C'

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=EVENT_RANGE).execute()
    event_data = result.get('values', [])
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=CATEGORIES_RANGE).execute()
    categories_data = result.get('values', [])

    # Vars
    HIGHLIGHTS = ['highlights']
    NORMAL = ['andrew', 'jenny', 'travel', 'work', 'life']
    CATEGORIES = HIGHLIGHTS + NORMAL

    categories = {'categories': CATEGORIES}
    temp = {}

    gallery_path = 'images/gallery/fulls/'

    # Utilities
    def extract_url(url):
        temp = urllib.request.urlopen(url)
        data = temp.read()
        datastring = data.decode("utf-8")
        m = re.search('https://lh3.google[^=]*', datastring)
        return m.group(0) + '=w3123-h2342'

    def store_image(title, url):
        p = gallery_path+title+'.jpg'
        if not os.path.exists(p):
            urllib.request.urlretrieve(url, p)
        im = Image.open(p)
        w, h = im.size
        if w/h > 4/3:
            hadjust = h % 3
            im1 = im.crop((w-4/3*(h-hadjust), hadjust, w, h))
            im1.save(p)
        return 'pages/story/'+p

    for c in CATEGORIES:
        categories[c] = {}
        temp[c]=[]

    # Load Categories into JSON
    if not categories_data:
        print('No data found.')
    else:
        for row in categories_data:
            categories[row[0]]['title'] = row[1]
            categories[row[0]]['summary'] = row[2]

    # Load Events into JSON
    if not event_data:
        print('No data found.')
    else:
        for row in event_data:

            # Store Image
            p = store_image(row[1], extract_url(row[5]))

            # Highlights
            if row[4]:
                temp[HIGHLIGHTS[0]].append({'date': row[0], 'title': row[1], 'summary': row[2], 'category': row[3], 'photo': p})

            # Normal Categories
            temp[row[3]].append({'date': row[0], 'title': row[1], 'summary': row[2], 'category': row[3], 'photo': p})

        # Store info sorted by date.
        for c in CATEGORIES:
            categories[c]['events'] = sorted(temp[c], key=lambda x: x['date'])

    print(categories)

    with open('categories.json', 'w') as json_file:
        json.dump({'root':categories}, json_file)

if __name__ == '__main__':
    main()
