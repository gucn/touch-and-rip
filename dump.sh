#!/bin/bash

# Dumps media files and the media library database from an iPod Touch.
# Tested to work when launched from zsh. Tested on iPod Touch 4th gen only.

DEST="$HOME/Desktop/iPod_dump" # Directory to save the dumped files

mkdir -p "$DEST" # Create directory if it doesn't exist
cd "$DEST"

# Generate the AFC client commands
(
echo "cd iTunes_Control"
echo "cd iTunes"
echo "get -r -f MediaLibrary.sqlitedb"
echo "cd /"
echo "cd iTunes_Control"
echo "cd Music"

# Find the number of music folders
max=$(echo -e "cd iTunes_Control\ncd Music\nls\nquit" | afcclient | grep -o 'F[0-9]\+' | sed 's/F//' | sort -n | tail -1)

# Dump each music folder
# Dump each music folder
for i in $(seq 0 "$max")
do
    # Check if folder exists before attempting download
    exists=$(echo -e "cd iTunes_Control\ncd Music\ncd F$(printf "%02d" "$i")\nls\nquit" \
        | afcclient 2>/dev/null)

    if [ -z "$exists" ]; then
        echo "Stopped: F$(printf "%02d" "$i") not found"
        break
    fi

    printf "get -r -f F%02d\n" "$i"
done

# Pipe to afcclient
echo "quit"
) | afcclient