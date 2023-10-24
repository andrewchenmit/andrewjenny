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
        if 'photos.app.goo.gl' in url:
            temp = urllib.request.urlopen(url)
            url_data = temp.read()
            datastring = url_data.decode("utf-8")
            m = re.search('https://lh3.google[^=]*', datastring)
            return m.group(0) + '=w3123-h2342'
        if 'pouch-nas' in url:
            return url

    def store_image(title, url):
        ext = '.webp'
        full = fulls_path+title+ext
        thumb = thumbs_path+title+ext

        if not os.path.exists(full):
            if 'pouch-nas' in url:
                try:
                  m = re.search('item_[^\?]*', url)
                  photo_id = m.group(0)[5:]
                except:
                  m = re.search('item/[^\?]*', url)
                  photo_id = m.group(0)[5:]
                m = re.search('sharing[^#]*', url)
                share_id = m.group(0)[8:]
                with open('pouchpass.json') as json_file:
                    json_data = json.load(json_file)
                    pouch_user = json_data['username']
                    pouch_pass = json_data['password']
                url = 'https://192-168-86-62.pouch-nas.direct.quickconnect.to:5001/mo/sharing/webapi/entry.cgi?api=SYNO.FotoTeam.Thumbnail&method=get&version=1&id='+photo_id+'&cache_key='+photo_id+'_1633659236&type=unit&size=xl'
                temp = urllib.request.urlopen('https://192-168-86-62.pouch-nas.direct.quickconnect.to:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=3&method=login&account='+pouch_user+'&passwd='+pouch_pass)
                url_data = temp.read()
                json_data = json.loads(url_data)
                sid = json_data['data']['sid']
                did = json_data['data']['did']
                pouch_request = urllib.request.Request(url)
                pouch_request.add_header("Cookie", "id="+sid)
                pouch_request.add_header("Cookie", "did="+did)
                pouch_request.add_header("x-syno-sharing", share_id)
                response = urllib.request.urlopen(pouch_request)
            else:
                response = urllib.request.urlopen(url)

            image = response.read()
            with open(full, "wb") as file:
                file.write(image)
            im = Image.open(full)
            w, h = im.size
            if w/h > 4/3:
                hadjust = h % 3
                neww = 4/3*(h-hadjust)
                wadjust = (w-neww) % 2
                new_im = im.crop(((w-(neww-wadjust))/2, hadjust, w-(w-(neww-wadjust))/2, h))
                new_im.save(full, format="webp")
            if w/h < 4/3:
                hadjust = h % 3
                newh = h - hadjust
                neww = int(newh * 4 / 3)
                wadjust = neww % 2
                leftw = int((neww - wadjust - w) / 2)

                new_im = Image.new("RGBA", (neww, newh), (0, 0, 0, 0))
                converted_im = im.convert("RGBA")
                new_im.paste(converted_im, (leftw, 0))

                new_im.save(full, format="webp")

        #if not os.path.exists(thumb):
            im = Image.open(full)
            new_im = im.resize((288, 216), Image.ANTIALIAS)
            new_im.save(thumb, optimize=True, format="webp", quality=90)

        return ['pages/story/'+full, 'pages/story/'+thumb]

    # Parent keys in data
    for c in CATEGORIES:
        data[c] = {}


    # Load last event list
    data_last = {}
    with open('data_last.json') as json_file:
        data_last = json.load(json_file)['root']

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

    repeat_data_count = 0
    new_data_count = 0
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
            if len(data_last) == 0 or row[1] not in data_last['events']:
                print('NEW DATA DETECTED')
                print(row)
                new_data_count += 1
                full_url, thumb_url = store_image(row[1], extract_url(row[5]))
            else:
                repeat_data_count += 1
                full_url = data_last['events'][row[1]]['full_url']
                thumb_url = data_last['events'][row[1]]['thumb_url']

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

    with open('data.json', 'w') as json_file:
        json.dump({'root':data}, json_file)
    with open('data_last.json', 'w') as json_file:
        json.dump({'root':data}, json_file)

    print('Done! Repeat rows: ', repeat_data_count, ' New rows: ', new_data_count)

if __name__ == '__main__':
    main()
