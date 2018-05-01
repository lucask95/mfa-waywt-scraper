# WAYWT Scraper

This script fetches the top 3 comments of each WAYWT post and outputs them to an HTML file. For now, the user must manually save the images and upload them to imgur. Later goals include automatic saving of images and automatic uploading of images to imgur.

You will need to set up your app on Reddit and create a praw.ini file for this to work. A praw.ini.bak file is included for you to use as a base for your praw.ini file. For a guide on how to do this, you may follow the instructions [here](http://pythonforengineers.com/build-a-reddit-bot-part-1/).

You will need to go to the [Reddit apps page](https://www.reddit.com/prefs/apps/) and create an app. This should not take more than a couple minutes. You will be given a client secret, which is labeled *secret* in the application information panel. You will also be given a client ID, which is located under the name and type of the application in the application information panel. You will need to copy those and paste those into the proper section in the praw.ini.bak file. Replace "CLIENT_ID_GOES_HERE" and "CLIENT_SECRET_GOES_HERE" with the actual ID and secret. You will also need to change the user agent. I made mine something along the lines of "WAYWT Script 1.0". Once you have done this, rename the praw.ini file to just "praw.ini".

Now you can run
