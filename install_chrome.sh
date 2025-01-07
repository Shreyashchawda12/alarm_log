#!/bin/bash

# Update and install prerequisites
apt-get update && apt-get install -y wget gnupg

# Download and install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/google-chrome.deb
apt-get install -y /tmp/google-chrome.deb || apt-get -f install -y
