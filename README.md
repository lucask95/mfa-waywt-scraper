# WAYWT Scraper

This script fetches the top 3 comments of each WAYWT post, outputs them to an HTML file, and saves them locally. Most images will be saved, but some images that are not hosted on imgur and/or not directly linked will not be saved. The user must check the saved images to see which ones are missing. Later goals include automatic uploading of the images to imgur.

## Set-Up Process

### Reddit App Setup

You will need to go to the [Reddit apps page](https://www.reddit.com/prefs/apps/) and create an app. This should not take more than a couple minutes. You will be given a client secret, which is labeled *secret* in the application information panel. You will also be given a client ID, which is located under the name and type of the application in the application information panel.

You will need to copy those and paste those into the proper section in the praw.ini.bak file. Replace "CLIENT_ID_GOES_HERE" and "CLIENT_SECRET_GOES_HERE" with the actual ID and secret. You will also need to change the user agent. I made mine something along the lines of "WAYWT Script 1.0". Once you have done this, rename the praw.ini file to just "praw.ini".

### Python Setup

To run this script, you must have Python 2.7 installed, as well as PRAW (the Python library to interact with Reddit's API) and BeautifulSoup for Python 2.

Download Python 2.7 from [here](https://www.python.org/downloads/) if you do not already have it. Download PRAW and BeautifulSoup by typing `pip install praw beautifulsoup4` on the command line. If you have Python 3 installed, you will instead need to type `pip2.7 install praw beautifulsoup4`.

### Running the Script

Open a command line window in the same directory as the script. On Windows, you can do this by holding shift and right-clicking, then selecting "Open PowerShell window here". Run the script by running fetcher.py with Python 2. On Windows, this is done by typing `py -2 .\fetcher.py`.

The script will output messages on the command line to update the user. When it is completely done fetching images, creating an HTML file, and saving images, it will open the created HTML file in your default web browser. When you are done checking saved images and saving the images that were not saved, you may close the command line window.
