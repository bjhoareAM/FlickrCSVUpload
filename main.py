import csv
import flickrapi

# Replace these with your actual Flickr API credentials.
API_KEY = 'your_api_key'
API_SECRET = 'your_api_secret'

# Use the absolute path to your CSV file on the desktop.
CSV_FILE = r'C:\Users\bjhoare\OneDrive - AUCKLAND MUSEUM\Desktop\Sailing Test Upload\Flickr Upload Testing.csv'

# Initialize the Flickr API client.
flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET, format='parsed-json')

# Authenticate with Flickr; if not already authenticated, this will guide you through the process.
if not flickr.token_valid(perms='write'):
    flickr.get_request_token(oauth_callback='oob')
    authorize_url = flickr.auth_url(perms='write')
    print("Open this URL in a browser to authorize the script:", authorize_url)
    verifier = input('Enter the verifier code: ')
    flickr.get_access_token(verifier)

def map_license_text_to_id(license_text):
    """
    Maps license text from the CSV to Flickr's numeric license ID.
    For example, 'no-known-copyright' maps to 10.
    """
    if license_text.lower() == 'no-known-copyright':
        return 10
    return 0  # Default to All Rights Reserved if no match is found

# Open and process the CSV file.
with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    # Adjust the delimiter if your CSV is comma-delimited instead of tab-delimited.
    reader = csv.DictReader(csvfile, delimiter='\t')
    for row in reader:
        # The CSV should contain absolute paths to the image files.
        filepath = row['filename']
        title = row['title']
        description = row['description']
        tags = row['tags']
        license_text = row.get('license', '')
        license_id = map_license_text_to_id(license_text)

        # Convert comma-separated tags from the CSV to space-separated tags for Flickr.
        tags_list = [tag.strip() for tag in tags.split(',')]
        tags_str = " ".join(tags_list)

        print(f"Uploading {filepath} with title '{title}'...")
        try:
            response = flickr.upload(
                filename=filepath,
                title=title,
                description=description,
                tags=tags_str,
                is_public=1,  # Adjust these parameters as needed
                is_friend=0,
                is_family=0,
                license=license_id
            )
            print("Upload successful! Response:", response)
        except Exception as e:
            print(f"Error uploading {filepath}: {e}")
