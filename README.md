# Flickr Uploader

This project is a Python-based script that uploads images to Flickr using a CSV file as input. The script reads image details (including file paths, titles, descriptions, tags, license info, album names, and system IDs) from a CSV file, uploads each image to Flickr, and logs the filename, system ID, and Flickr photo ID for each successful upload.

## Overview

**Purpose:**  
Automate the upload of images to Flickr using data provided in a CSV file.

**Features:**
- Reads image details from a CSV file.
- Uploads images to Flickr with provided metadata (title, description, tags, etc.).
- Logs concise messages (file name, system ID, and photo ID) for each successful upload.
- Associates images with albums if specified in the CSV.

## Prerequisites

- **Python 3.x**
- **flickrapi** package  
  Install via pip:
  ```bash
  pip install flickrapi
  ```
- A valid Flickr API key and secret, stored in `flickrAuthData.txt` with the API key on the first line and the API secret on the second line.

## CSV File Format

Your CSV file **must** contain the following columns (header row). The script expects these exact column names:

1. **system_id** (string or numeric)  
   - Internal system ID used only for logging or reference.  
   - Not sent to Flickr.

2. **filename** (string)  
   - The full path to the image file on your system.  
   - **Example:**  
     `[INSERT FULL PATH HERE]\PH-2013-7-TC-B862-08.jpg`

3. **title** (string)  
   - The title you want to assign to the image on Flickr.  
   - **Example:**  
     `[Boat "Ozone" by old sailing ship]`

4. **description** (multi-line string allowed)  
   - A detailed description of the image.  
   - Can include line breaks; if so, enclose the field in quotes.  
   - **Example:**
     ```csv
     "View of two men on-board a fishing boat, ""OZONE"".
     A big game fish is lying on the stern of the boat."
     ```
   - When editing in Excel, wrap the entire cell in quotes if it contains commas, quotes, or new lines.

5. **tags** (comma-separated list)  
   - Tags you want to assign to the photo, separated by commas.  
   - The script converts them to space-separated tags for Flickr.  
   - **Example:**  
     `Sailing, Sailboats, Documentary Heritage, Gelatin Silver Print`

6. **license** (string)  
   - License information.  
   - For example, `"no-known-copyright"` maps to Flickr’s numeric license ID (10).

7. **album** (string, optional)  
   - The name of the Flickr album (photoset) where you want the photo to appear.  
   - If the album doesn’t exist, the script creates it.

### Example CSV Snippet

Below is a sample row demonstrating the structure. Notice how the `description` column spans multiple lines within quotes:

```csv
system_id,filename,title,description,tags,license,album
1048694,"C:\Users\bjhoare\OneDrive - AUCKLAND MUSEUM\Desktop\Sailing Test Upload\PH-2013-7-TC-B862-08.jpg","[Boat ""Ozone"" by old sailing ship]","View of two men on-board a fishing boat, ""OZONE"". A big game fish is lying on the stern of the boat. A large boat, possibly a scow, is in the background. Gelatin dry plate negative photograph by Mr Tudor Washington Collins (Warkworth).
Part of the Documentary Heritage Collection
Credit Line: Collection of Auckland War Memorial Museum, No known copyright restrictions, 1048694
For more details visit https://www.aucklandmuseum.com/discover/collections/record/1048694","Sailing, Sailboats, Documentary Heritage, Gelatin Silver Print","no-known-copyright","upload test"
```

**Tips for Creating/Editing the CSV:**
- Use UTF-8 (or UTF-8 with BOM) encoding, especially if you have special characters.
- When editing the file in Excel, ensure it’s saved as a CSV (Comma Delimited) file.
- Escape quotes within fields by doubling them: `""`.

## Configuration

1. **flickrAuthData.txt**  
   Create or update the `flickrAuthData.txt` file in the project root with your Flickr API credentials:
   ```
   your_api_key
   your_api_secret
   ```

2. **CSV File**  
   In the `uploader.py` script, update the `CSV_FILE` variable with the full path to your CSV file. For example:
   ```python
   CSV_FILE = r"[YOUR LOCAL FILEPATH HERE].csv"
   ```

## Usage

1. **Run the Script:**  
   From your terminal or command prompt, run:
   ```bash
   python uploader.py
   ```
   If you have not authenticated previously, you’ll be prompted to open a browser and authorize the application with Flickr. Enter the verifier code when prompted.

2. **Logging:**  
   A concise log is written to `upload_log.txt` containing the filename, system ID, and Flickr photo ID for each successfully uploaded image.

## Troubleshooting

- **File Not Found:**  
  Verify that the file paths in your CSV are correct and that the images exist on your system.

- **Authentication Issues:**  
  Ensure that your `flickrAuthData.txt` file is correctly formatted with your API credentials and that you’ve authorized the script if prompted.

- **Invalid CSV Format:**  
  Confirm that your CSV is UTF-8 encoded and that each field is properly quoted if it contains commas or new lines.

- **Missing Columns:**  
  Make sure your CSV header row includes `system_id, filename, title, description, tags, license, album`.
