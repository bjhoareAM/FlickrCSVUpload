import csv
import flickrapi
import time
import sys
import os
import logging
from xml.etree import ElementTree as ET

# Set up logging to only capture INFO and higher.
logging.basicConfig(
    filename='upload_log.txt',
    filemode='a',  # Append mode
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Suppress verbose logging from flickrapi.
logging.getLogger('flickrapi').setLevel(logging.ERROR)
logging.getLogger('flickrapi.flickr_api').setLevel(logging.ERROR)
logging.getLogger('flickrapi.REST').setLevel(logging.ERROR)

def read_flickr_auth(filename='flickrAuthData.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        if len(lines) < 2:
            raise ValueError("flickrAuthData.txt must contain at least two lines: API key and API secret.")
        return lines[0].strip(), lines[1].strip()
    except Exception as e:
        logging.error("Error reading credentials: %s", e)
        return None

# Read API credentials.
creds = read_flickr_auth()
if creds is None:
    sys.exit("Failed to read Flickr credentials.")
API_KEY, API_SECRET = creds

# Initialize Flickr API client.
flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET, format='parsed-json')

# Authenticate with Flickr if needed.
if not flickr.token_valid(perms='write'):
    flickr.get_request_token(oauth_callback='oob')
    authorize_url = flickr.auth_url(perms='write')
    print("Open this URL in a browser to authorize the script:", authorize_url)
    verifier = input('Enter the verifier code: ')
    flickr.get_access_token(verifier)

def map_license_text_to_id(license_text):
    return 10 if license_text.lower() == 'no-known-copyright' else 0

# CSV file path on your desktop.
CSV_FILE = r"C:\Users\bjhoare\OneDrive - AUCKLAND MUSEUM\Desktop\Sailing Test Upload\Flickr Upload Testing.csv"

# Retrieve existing albums (if needed).
try:
    existing_albums_response = flickr.photosets.getList()
    existing_albums = existing_albums_response.get('photosets', {}).get('photoset', [])
    album_map = {album['title']['_content']: album['id'] for album in existing_albums}
except Exception as e:
    album_map = {}

with open(CSV_FILE, newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        filepath    = row.get('filename', '').strip().strip('"')
        title       = row.get('title', '').strip().strip('"')
        description = row.get('description', '').strip().strip('"')
        tags        = row.get('tags', '').strip().strip('"')
        license_val = row.get('license', '').strip().strip('"')
        album_name  = row.get('album', '').strip().strip('"')
        system_id   = row.get('system_id', '').strip().strip('"')  # Extra field for logging

        # Check that the file exists.
        if not os.path.exists(filepath):
            print(f"Error: file does not exist: {filepath}. Skipping this row.")
            continue

        license_id = map_license_text_to_id(license_val)
        tags_list = [tag.strip() for tag in tags.split(',')]
        tags_str = " ".join(tags_list)

        print(f"Uploading {filepath} (system ID: {system_id})...")
        try:
            response = flickr.upload(
                filename=filepath,
                title=title,
                description=description,
                tags=tags_str,
                is_public=1,
                is_friend=0,
                is_family=0,
                license=license_id,
                format='rest'
            )

            # Convert response to XML.
            if isinstance(response, bytes):
                xml_response = ET.fromstring(response)
            else:
                xml_response = response

            photoid_elem = xml_response.find('photoid')
            if photoid_elem is None or not photoid_elem.text:
                print(f"Error uploading {filepath}: invalid Flickr response.")
                continue

            photo_id = photoid_elem.text
            # Log only the successful upload info.
            logging.info("Successfully uploaded: %s (system ID: %s, Photo ID: %s)", filepath, system_id, photo_id)
            print(f"Upload successful for {filepath} (system ID: {system_id})! Photo ID: {photo_id}")

            # Album association if specified.
            if album_name:
                if album_name in album_map:
                    photoset_id = album_map[album_name]
                    flickr.photosets.addPhoto(photoset_id=photoset_id, photo_id=photo_id)
                else:
                    create_response = flickr.photosets.create(title=album_name, primary_photo_id=photo_id)
                    photoset_id = create_response['photoset']['id']
                    album_map[album_name] = photoset_id
        except Exception as e:
            print(f"Error uploading {filepath} (system ID: {system_id}): {e}")

        # Throttle uploads.
        time.sleep(1)

print("Script terminated successfully.")
sys.exit(0)
