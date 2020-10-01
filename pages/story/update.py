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
EVENT_RANGE = 'Story!A2:G'
CATEGORIES_RANGE = 'Categories!A2:C'

def main():
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

    fulls_path = 'images/gallery/fulls/'
    thumbs_path = 'images/gallery/thumbs/'

    # Utilities
    def extract_url(url):
        temp = urllib.request.urlopen(url)
        url_data = temp.read()
        datastring = url_data.decode("utf-8")
        m = re.search('https://lh3.google[^=]*', datastring)
        return m.group(0) + '=w3123-h2342'

    def store_image(title, url):
        full = fulls_path+title+'.png'
        thumb = thumbs_path+title+'.png'

        if not os.path.exists(full):
            urllib.request.urlretrieve(url, full)
            im = Image.open(full)
            w, h = im.size
            if w/h > 4/3:
                hadjust = h % 3
                neww = 4/3*(h-hadjust)
                wadjust = (w-neww) % 2
                new_im = im.crop(((w-(neww-wadjust))/2, hadjust, w-(w-(neww-wadjust))/2, h))
                new_im.save(full)
            if w/h < 4/3:
                hadjust = h % 3
                newh = h - hadjust
                neww = int(newh * 4 / 3)
                wadjust = neww % 2
                leftw = int((neww - wadjust - w) / 2)

                new_im = Image.new("RGBA", (neww, newh), (0, 0, 0, 0))
                converted_im = im.convert("RGBA")
                new_im.paste(converted_im, (leftw, 0))

                new_im.save(full)

        #if not os.path.exists(thumb):
            im = Image.open(full)
            new_im = im.resize((288, 216), Image.ANTIALIAS)
            new_im.save(thumb, optimize=True)

        return ['pages/story/'+full, 'pages/story/'+thumb]

    # Parent keys in data
    for c in CATEGORIES:
        data[c] = {}

    # Load Categories into JSON
    if not categories_data:
        print('No data found.')
    else:
        for row in categories_data:
            data[row[0]]['title'] = row[1]
            data[row[0]]['event_titles'] = []
            try:
                data[row[0]]['summary'] = row[2]
            except:
                continue

    # Load Events into JSON
    if not event_data:
        print('No data found.')
    else:
        event_list = []
        temp_years = []

        # Load event data
        for row in event_data:
            if len(row) == 7:
                album_url = row[6]
            else:
                album_url = ''

            # Store Image
            full_url, thumb_url = store_image(row[1], extract_url(row[5]))
            event = {'date': row[0], 'title': row[1], 'summary': row[2], 'category': row[3], 'highlight': row[4], 'full_url': full_url, 'thumb_url': thumb_url, 'album_url': album_url}
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
                data[HIGHLIGHTS[0]]['event_titles'].append(event['title'])

            # Normal Categories
            data[event['category']]['event_titles'].append(event['title'])

            # Event Repository keyed by Title
            data['events'][event['title']] = event

            # Years
            year = event['date'][0:4]
            data[year]['event_titles'].append(event['title'])

    print(data)

    with open('data.json', 'w') as json_file:
        json.dump({'root':data}, json_file)

if __name__ == '__main__':
    main()
