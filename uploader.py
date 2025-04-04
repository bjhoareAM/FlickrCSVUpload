import csv
import flickrapi
import time
import sys
import os
import logging
from xml.etree import ElementTree as ET

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

def read_flickr_auth(filename='flickrAuthData.txt'):
    """
    Reads Flickr API credentials from a text file.
    The file should have the API key on the first line and the API secret on the second.
    """
    logging.debug(f"Trying to open {filename}")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        logging.debug("lines = %s", lines)
        if len(lines) < 2:
            raise ValueError("flickrAuthData.txt must contain at least two lines: API key and API secret.")
        api_key = lines[0].strip()
        api_secret = lines[1].strip()
        logging.debug("API_KEY = %s, API_SECRET = %s", api_key, api_secret)
        return api_key, api_secret
    except Exception as e:
        logging.error("Error reading file: %s", e)
        return None

# Read API credentials
creds = read_flickr_auth()
if creds is None:
    sys.exit("Failed to read Flickr credentials.")
API_KEY, API_SECRET = creds

# Initialize Flickr API client with default JSON format for other calls.
flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET, format='parsed-json')

# Authenticate with Flickr (this will prompt for a verifier if a valid token isn't available)
if not flickr.token_valid(perms='write'):
    flickr.get_request_token(oauth_callback='oob')
    authorize_url = flickr.auth_url(perms='write')
    print("Open this URL in a browser to authorize the script:", authorize_url)
    verifier = input('Enter the verifier code: ')
    flickr.get_access_token(verifier)

def map_license_text_to_id(license_text):
    """
    Maps a license text from the CSV to Flickr's numeric license ID.
    """
    if license_text.lower() == 'no-known-copyright':
        return 10
    return 0

# Update the CSV_FILE path to your actual file
CSV_FILE = r"C:\Users\bjhoare\OneDrive - AUCKLAND MUSEUM\Desktop\Sailing Test Upload\Flickr Upload Testing.csv"

# Get existing albums (photosets) so we don't create duplicates
try:
    existing_albums_response = flickr.photosets.getList()
    existing_albums = existing_albums_response.get('photosets', {}).get('photoset', [])
    album_map = {album['title']['_content']: album['id'] for album in existing_albums}
    logging.debug("Existing albums: %s", album_map)
except Exception as e:
    logging.error("Error retrieving existing albums: %s", e)
    album_map = {}

# Open the CSV using 'utf-8-sig' to handle BOM issues
with open(CSV_FILE, newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        logging.debug("DEBUG ROW: %s", row)
        # Remove extra double quotes from each field
        filepath = row.get('filename', '').strip().strip('"')
        title = row.get('title', '').strip().strip('"')
        description = row.get('description', '').strip().strip('"')
        tags = row.get('tags', '').strip().strip('"')
        license_value = row.get('license', '').strip().strip('"')
        album_name = row.get('album', '').strip().strip('"')

        # Check that the file exists
        if not os.path.exists(filepath):
            logging.error("Error: file does not exist: %s. Skipping this row.", filepath)
            continue

        license_id = map_license_text_to_id(license_value)

        # Convert comma-separated tags to space-separated tags for Flickr
        tags_list = [tag.strip() for tag in tags.split(',')]
        tags_str = " ".join(tags_list)

        logging.info("Uploading %s with title '%s'...", filepath, title)
        try:
            # Pass format='rest' so the upload returns XML instead of JSON
            response = flickr.upload(
                filename=filepath,
                title=title,
                description=description,
                tags=tags_str,
                is_public=1,  # Adjust if needed
                is_friend=0,
                is_family=0,
                license=license_id,
                format='rest'
            )

            # Handle response which may be bytes or an XML element
            if isinstance(response, bytes):
                raw_response = response.decode('utf-8')
                xml_response = ET.fromstring(response)
            else:
                raw_response = ET.tostring(response, encoding='utf-8').decode('utf-8')
                xml_response = response

            logging.debug("Raw upload response: %s", raw_response)

            # Check if response is empty or doesn't contain photoid
            photoid_elem = xml_response.find('photoid')
            if photoid_elem is None or not photoid_elem.text:
                logging.error("Error: Flickr API returned an empty or invalid response.")
                continue
            photo_id = photoid_elem.text
            logging.info("Upload successful! Photo ID: %s", photo_id)

            # If an album name is specified, add the photo to the album
            if album_name:
                if album_name in album_map:
                    photoset_id = album_map[album_name]
                    add_response = flickr.photosets.addPhoto(photoset_id=photoset_id, photo_id=photo_id)
                    logging.info("Added photo %s to existing album '%s'.", photo_id, album_name)
                else:
                    create_response = flickr.photosets.create(title=album_name, primary_photo_id=photo_id)
                    photoset_id = create_response['photoset']['id']
                    album_map[album_name] = photoset_id
                    logging.info("Created new album '%s' with photo %s as primary.", album_name, photo_id)
        except Exception as e:
            logging.exception("Error uploading %s: %s", filepath, e)
        # Throttle uploads to avoid hitting rate limits
        time.sleep(1)

print("Script terminated successfully.")
sys.exit(0)
