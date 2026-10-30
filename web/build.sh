#!/bin/sh
# Copy the JavaScript port next to index.html, so the page works as a static site.
set -e
cd "$(dirname "$0")"
rm -rf nutq
cp -R ../js/src nutq
echo "copied js/src -> web/nutq"
