# This code takes the output files of the dump.sh script and
# reorganises them into orderly folders of Artist and Album names

# Please adjust the config.txt as desired before running this
# DB= the path of the MediaLibrary.sqlitedb file dumped by dump.sh (~/Desktop/iPod_dump unless changed)
# ROOT= should be where the song files were dumped by dump.sh (~/Desktop/iPod_dump unless changed)
# OUTPUT= desired output location  (~/Desktop/iPod_music unless changed)

import os
import sqlite3
import shutil

# Helper to sanitise and normalise metadata strings
def clean_text(value, fallback=None):
    value = (value or "").strip()

    if not value:
        return fallback

    return "".join(c for c in value if c not in r'\/:*?"<>|')

# Helper to load the config file with directories

def load_config(path):
    config = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            config[key.strip()] = os.path.expandvars(value.strip())

    return config


config = load_config("config.txt")


DB = config["DB"]           # Database of media metadata
ROOT = config["ROOT"]       # Directory with dumped files
OUTPUT = config["OUTPUT"]   # Output directory for reorganised files


seen_files = set()          # Path/file pair tracker to avoid dupes

os.makedirs(OUTPUT, exist_ok=True)

# Connect to the SQLite database of media metadata
conn = sqlite3.connect(DB)
cur = conn.cursor()

# Query the music items and join metadata tables
cur.execute("""
SELECT
  item_extra.title,
  item_extra.location,
  base_location.path,
  item_artist.item_artist,
  album.album,
  item.track_number
FROM item_extra
JOIN item ON item_extra.item_pid = item.item_pid
JOIN base_location ON item.base_location_id = base_location.base_location_id
LEFT JOIN item_artist ON item.item_artist_pid = item_artist.item_artist_pid
LEFT JOIN album ON item.album_pid = album.album_pid
WHERE item_extra.media_kind = 1
  AND item_extra.is_podcast = 0
  AND item_extra.is_itunes_u = 0
  AND item_extra.is_audible_audio_book = 0
""")

rows = cur.fetchall()
conn.close()

renamed = 0             # Counters to report if any
unchanged = 0           # files couldn't be renamed


for title, filename, path, artist, album, track_number in rows:

    print("PROCESSING:", title, filename, path)

    file_key = os.path.join(path, filename)     # Make the file/path pair to identify dupes

    if file_key in seen_files:
        continue

    seen_files.add(file_key)

    folder = os.path.basename(path)             # Extract folder name from iTunes-style path
    src = os.path.join(ROOT, folder, filename)  # Construct full source path

    if not os.path.isfile(src):
        unchanged += 1
        continue

    # Extract track number for file ordering
    # Note: fractional track numbers (e.g interludes) are treated as null
    # because my library includes no such songs & I can't test that
    try:
        track_num = int(track_number)
    except (TypeError, ValueError):
        track_num = None

    # Values to use if any metadata field or title is empty
    safe_artist = clean_text(artist, "Unknown Artist")
    safe_album = clean_text(album, "Unknown Album")

    raw_title = (title or "").strip()

    # Create title to fall back on from the dumped file's name
    if raw_title == "":
        blob_base = os.path.splitext(filename)[0]
        fallback_id = blob_base[:4] if blob_base else "XXXX"
        safe_title = f"Untitled_{fallback_id}"
    else:
        safe_title = clean_text(raw_title)    

    # Create directories to organise tracks into
    artist_dir = os.path.join(OUTPUT, safe_artist)
    album_dir = os.path.join(artist_dir, safe_album)

    os.makedirs(album_dir, exist_ok=True)

    file_ext = os.path.splitext(filename)[1] # Extract source extension

    # [no longer needed] Preserve None vals for missing track numbers
    # track_num = None if track_num is None else track_num

    # If track number exists prepend it to the file name
    prefix = f"{track_num:02d} - " if isinstance(track_num, int) else ""
    # Comment out the above line to omit track number prefixes

    # Construct final file destination
    dst = os.path.join(album_dir, prefix + safe_title + file_ext)

    i = 1                               # Initialise dupe counter
    base, ext = os.path.splitext(dst)   # Prep base path for dupe handling

    while os.path.exists(dst):
        dst = f"{base} ({i}){ext}"      # Avoid overwriting collisions
        i += 1

    shutil.copy2(src, dst)              # Copy file from source to desination
    renamed += 1

print("Done")
print("Renamed:", renamed)
print("Missing files:", unchanged)