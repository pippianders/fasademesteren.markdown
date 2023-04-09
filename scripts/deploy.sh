#!/bin/bash

# FIXME Copy me to hugo site root directory

# Rebuild md notes
python3 "markdown2hugo.py" ~/notes ./content ./static/img

# Generate index files, required by hugo-theme-learn
hugo new --kind index _index.md 2> /dev/null
find ./content -type d -mindepth 1 -exec hugo new --kind chapter {}/_index.md \;  2> /dev/null

# rebuild page
hugo
