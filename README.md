# touch-and-rip
iPod Touch Music Extractor

This project extracts music files from an iPod Touch filesystem dump and reconstructs a structured music library on disk using metadata from the device’s iTunes database.

It consists of:

dump.sh -> connects to the device and extracts:
			MediaLibrary.sqlitedb
			music files stored in /iTunes_Control/Music
rename.py -> rebuilds folder structure using metadata
config.txt -> user configuration for paths

Requirements

* macOS or Linux (Windows may require minor path adjustments)
* Python 3.x
* afcclient available in PATH
* iPod Touch filesystem access via AFC (Works on a vanilla iPod Touch 4th Gen with software version 6.1.5. Newer devices might require additional privileges.)

Workflow

The process runs in two stages:

1. Dump files from iPod
dump.sh connects to the device and extracts:
	MediaLibrary.sqlitedb
	music files stored in /iTunes_Control/Music

Output is placed into a local folder.

2. Rebuild library structure
rename.py:
	reads MediaLibrary.sqlitedb
	matches files from the dump
	sanitises metadata (artist, album, title)
	renames and organises files into a structured music library

OUTPUT/
Artist/
Album/
TrackNumber - Title.mp3

Setup

1. Configure paths

Edit config.txt:

	DB=$HOME/Desktop/iPod_dump/MediaLibrary.sqlitedb
	ROOT=$HOME/Desktop/iPod_dump
	OUTPUT=$HOME/Desktop/iPod_music

Fields:

	DB -> path to the extracted iTunes database
	ROOT -> directory containing dumped iPod files
	OUTPUT -> destination music library


2. Run dump script

bash dump.sh

This will extract:

	music database
	raw audio files

*****************************************************************
*	If you don't want the structured library you can stop here.	  *
*	Note that your file names will be unrecognisable.			        *
*****************************************************************

3. Rebuild library

python3 rename.py

Output structure

OUTPUT/
Artist Name/
Album Name/
01 - Song.mp3
02 - Song.mp3

Files are:

	renamed using metadata
	grouped by artist and album
	sanitised for filesystem safety
	deduplicated if conflicts exist

Notes

* This tool assumes a standard iTunes/iPod Touch music database structure
* Designed for personal library recovery, not streaming sync nor file sharing
* I have only tested it on an iPod Tough 4th Gen with software update 6.1.5 as I have no other device
* This tool is provided with absolutely no warranty

License

This project is licensed under the MIT License. See LICENSE file for details.

Possible improvements

- Add hash-based file verification for duplicate detection
  (currently duplicates are detected using path + filename matching)
