#!/bin/bash

# Get the current date in YYYY-MM-DD format
date=$(date +%Y-%m-%d)

# Set the source file and destination directory
src_file="/michigan_melee_bot/Michigan-Melee-Slippi-Ranked-Bot/database.db"
dest_dir="/michigan_melee_bot/Michigan-Melee-Slippi-Ranked-Bot/"

# Create a new filename with the current date
filename=$(basename "$src_file")
extension="${filename##*.}"
filename="${filename%.*}_$date.$extension"
dest_file="$dest_dir/$filename"

# Copy the file to the destination directory with the new name
cp "$src_file" "$dest_file"

# Transfer the file to the remote server using scp
remote_user="username"
remote_host="remote.server.com"
remote_dir="/path/to/remote/directory"
scp "$dest_file" "$remote_user@$remote_host:$remote_dir"
