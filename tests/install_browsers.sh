#!/bin/bash -ex

export DEBIAN_FRONTEND="noninteractive"

HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TMP=$(mktemp -d)

cd $TMP

apt-get -qq update > /dev/null

# get dependencies
apt-get -yqq install unzip > /dev/null

# get firefox and dependencies
apt-get -yqq install firefox  > /dev/null

# get geckodriver
wget -q https://github.com/mozilla/geckodriver/releases/download/v0.19.1/geckodriver-v0.19.1-linux64.tar.gz -O geckodriver.tar.gz
tar xzvf geckodriver.tar.gz
cp --no-preserve=ownership geckodriver $HERE/bin

# get chromedriver
wget -q https://chromedriver.storage.googleapis.com/2.33/chromedriver_linux64.zip -O chromedriver.zip
unzip chromedriver.zip
cp --no-preserve=ownership chromedriver $HERE/bin

# get chrome
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
( dpkg -i google-chrome-stable_current_amd64.deb || apt -yqqf install ) > /dev/null

cd $HERE
rm -rf TMP

if [ ! -L bin/google-chrome ]; then
    ln -s `which google-chrome-stable` bin/google-chrome
fi
