#!/bin/sh

mkdir -p ./data
cached_file=./data/cached_features.zip
cached_file_id=1xJ1KiVYh2GjIbFsLu5oJhbrS5cNVqRfX

rm -f $cached_file
rm -rf ./data/cached_features

python download_ggdriver.py --unzip $cached_file_id $cached_file
