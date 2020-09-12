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

    data = {'categories': CATEGORIES, 'years': [], 'events': {}}
    temp = {}

    gallery_path = 'images/gallery/fulls/'

    # Utilities
    def extract_url(url):
        temp = urllib.request.urlopen(url)
        url_data = temp.read()
        datastring = url_data.decode("utf-8")
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

    # Parent keys in data
    for c in CATEGORIES:
        data[c] = {}
        temp[c] = []

    # Load Categories into JSON
    if not categories_data:
        print('No data found.')
    else:
        for row in categories_data:
            data[row[0]]['title'] = row[1]
            data[row[0]]['summary'] = row[2]
            data[row[0]]['event_titles'] = []

    # Load Events into JSON
    if not event_data:
        print('No data found.')
    else:
        event_list = []
        temp_years = []

        # Load event data
        for row in event_data:

            # Store Image
            p = store_image(row[1], extract_url(row[5]))
            event = {'date': row[0], 'title': row[1], 'summary': row[2], 'category': row[3], 'highlight': row[4], 'photo': p}
            event_list.append(event)

            year = row[0][0:4]
            if not year in temp_years:
                temp_years.append(year)

        # Sort years from future to past
        data['years'] = sorted(temp_years, reverse=True)

        for year in data['years']:
            data[year] = {'event_titles': []}


        # Sort earliest to latest
        sorted_events = sorted(event_list, key=lambda x: x['date'])

        # Store titles per category
        for event in sorted_events:

            # Highlights
            if event['highlight']:
                temp[HIGHLIGHTS[0]].append(event['title'])

            # Normal Categories
            print(temp[row[3]])
            temp[row[3]].append(event['title'])

            # Event Repository keyed by Title
            data['events'][event['title']] = event

            # Years
            year = event['date'][0:4]
            data[year]['event_titles'].append(event['title'])

        # Store date-sorted event keys by category
        for c in CATEGORIES:
            print(temp[c])
            data[c]['event_titles'] = temp[c]

        # Sort years from future to past
        data['years'] = sorted(temp_years, reverse=True)

        print(data['years'])

    print(data)

    with open('data.json', 'w') as json_file:
        json.dump({'root':data}, json_file)

if __name__ == '__main__':
    main()
