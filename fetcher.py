# dependencies that must be installed
from bs4 import BeautifulSoup
import praw

# default libraries
from time import sleep
import datetime
import os
import re
import requests
import SimpleHTTPServer
import SocketServer
import sys
import urllib
import webbrowser


# variables and constants
# ----------------------------------------
HTML_FILENAME = 'index.html'
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
COMMENTS_TO_SCRAPE = 3 # number of comments to grab from each thread


# functions
# ----------------------------------------

# returns list of tuples of links in the format (link text, url)
def get_links(body_text):
    body_text = u''.join(body_text).encode('utf-8')
    # regex match markdown links and raw pasted links from imgur
    regex_md = r'\[(.+?)\]\s*\((.+?)\)'
    regex_rawpaste = r'https*:\/\/(?:i\.)*imgur.com\/[^\)\n]*(?![^\(\)]*\))'
    matches_md = re.findall(regex_md, body_text)
    matches_rawpaste = re.findall(regex_rawpaste, body_text)

    matches = []
    for m in matches_md:
        matches.append(m)
    for m in matches_rawpaste:
        matches.append((str(m), m))

    return matches


# writes proper html formatting to file
def initialize_html(filename):
    with open(filename, 'w') as f:
        f.write('<html>\n<head>\n<title>Top of WAYWT</title>\n<link rel="stylesheet" href="style.css"></head>\n<body>\n')
    return


# finish off the html document
def finalize_html(filename):
    with open(filename, 'a') as f:
        f.write('</body>\n</html>')
    return


# saves images to folder
def save_image(url, image_name):
    # check if images directory exists. if it does not, create it
    base_dir = os.path.dirname(os.path.realpath(__file__))
    dir_name = os.path.join(base_dir, 'images')
    if not os.path.exists(dir_name) or not os.path.isdir(dir_name):
        print '"/images/" directory does not exist. creating directory "/images/"'
        os.makedirs(dir_name)

    try:
        # if url ends with jpg or png, just save the image
        if url.endswith('.jpg') or url.endswith('.png'):
            # url[-4:] gets the last 4 characters of the url
            image_name = './images/' + image_name + url[-4:]
            urllib.urlretrieve(url, image_name)

        # if url is not a directly-linked image, and is an imgur url,
        # get the first image from the imgur page
        elif 'imgur.com' in url:
            result = requests.get(url)
            if result.status_code == 200:
                soup = BeautifulSoup(result.content, 'html.parser')

                # this finds all the images in the album that are loaded upon
                # the first request
                samples = soup.find_all('img', {'itemprop': 'contentURL'})

                if len(samples) > 0:
                    image_src = 'https:' + samples[0].attrs['src']
                    if image_src.endswith('.jpg') or url.endswith('.png'):
                        image_name = './images/' + image_name + image_src[-4:]
                        urllib.urlretrieve(image_src, image_name)
                else:
                    # just in case there are no images able to be found
                    print 'Unable to save image', image_name

            # if result is not 200
            else:
                print 'Unable to save image', image_name

        # if not directly linked image, and not from imgur
        else:
            print 'Unable to save image', image_name

    # if directory does not exist, ioerror gets thrown
    except IOError:
        print 'Directory "/images/" does not exist. Please create this directory and then run this script again.'
        sys.exit(0)

    # sleep for half a second so we're not sending too many requests to imgur
    sleep(0.5)
    return


# creates a div for each top post of the month in the html file
def write_to_html(index, comment, filename):
    # convert unicode text
    links = get_links(comment.body)

    # convert seconds since epoch timestamp to proper date format
    fmt = "%B %d %Y"
    date = datetime.datetime.fromtimestamp(comment.created).strftime(fmt)

    # file context manager for easy closing of file
    with open(filename, 'a') as f:
        # write commenter /u/, permalink, and date to file
        f.write('<div class="box1">\n/u/' + str(comment.author) + '<br />\n')
        f.write('<a href="https://reddit.com' + str(comment.permalink) + '">Link to Comment</a><br />\n')
        f.write(date + '<br />\n<p></p>\n')

        if len(links) == 0:
            print 'Unable to save image', str(index + 1)

        # write each link to file
        # if direct link to imgur image, write to <img> tag, otherwise to <a> tag
        for i, a in enumerate(links):
            text = a[0]
            url = a[1]

            # saves image if it's the first link in a post
            if i == 0:
                save_image(url, str(index + 1))

            # if url is an imgur album
            if 'imgur.com/a/' in url:
                regex = r'imgur.com\/(a\/([\w\d]+))'
                match = re.search(regex, url)
                f.write('<blockquote class="imgur-embed-pub" lang="en" data-id="' + match.group(1) + '">')
                f.write('<a href="http://imgur.com/' + match.group(2) + '"></a>')
                f.write('</blockquote><script async src="http://s.imgur.com/min/embed.js" charset="utf-8"></script>\n<br />\n')

            # if url is an image on imgur
            elif 'imgur' in url and url.endswith(('.jpg', '.jpeg', '.png')):
                f.write('<img src="' + url + '" alt="' + text +'"><br />\n')

            # if an imgur url and not a direct image nor an album
            elif 'imgur' in url and not url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.gifv')):
                regex = r'imgur.com/([\w\d]+)'
                match = re.search(regex, url)
                f.write('<blockquote class="imgur-embed-pub" lang="en" data-id="' + match.group(1) + '">')
                f.write('<a href="http://imgur.com/' + match.group(1) + '"></a>')
                f.write('</blockquote><script async src="http://s.imgur.com/min/embed.js" charset="utf-8"></script>\n<br />\n')

            # if not an imgur url, just make a normal link
            else:
                f.write('<a href="' + url + '">' + text + '</a><br />\n')

        # close off div for comment
        f.write('</div>\n')

    return


# writes <code> block to the html file specified by filename
def write_codebox(comments, filename):

    # file context manager for easy closing of file
    with open(filename, 'a') as f:
        f.write('<div class="box1">\n<h3>Info Comment Markup</h3>\n<div class="code"><code>\n')

        for i, comment in list(enumerate(comments)):
            s = str(comment.author)

            # don't write a /u/ before the name if the user has deleted their account
            if s == 'None':
                s = '[deleted]'
            else:
                s = '/u/' + s

            # first line formatted like: 1. Post by /u/Smilotron (+50)
            f.write(str(i + 1) + '.[Post](https://reddit.com' + str(comment.permalink) + ') by *' + s + '* (+' + str(comment.ups) + ')<br /><br >\n')

            # second line formatted like: Link 1, Link 2, Link 3, ...
            for j, a in list(enumerate(get_links(comment.body))):
                if j > 0:
                    f.write(', ')
                f.write('[Link ' + str(j + 1) + '](' + a[1] + ')')

            # end of the second line (the line with the links)
            f.write('<br /><br />\n')

        # end of the code box
        f.write('</code></div>\n</div>\n')

    return


# ---------------------------------------------------------------------------- #
#
#                        Beginning of non-function code
#
# ---------------------------------------------------------------------------- #


# user input of month to scrape
# ----------------------------------------
try:
    month_num = int(input('\nEnter the number of the month you wish to scrape: '))
    month_index = month_num - 1
    month_to_scrape = MONTHS[int(month_index)]
    print('Getting top posts from ' + month_to_scrape)
except TypeError:
    print('Please enter an integer from 1 to 12')
except IndexError:
    print('Please enter an integer from 1 to 12')
except:
    print('Unexpected error: ', sys.exc_info()[0])
    sys.exit(0)


# set up praw and get threads to scrape
# ----------------------------------------
reddit = praw.Reddit('waywtbot')
mfa_subreddit = reddit.subreddit('malefashionadvice')
waywt_threads = mfa_subreddit.search('waywt ' + month_to_scrape, sort='new', syntax='lucene', time_filter='year')
print('Retreived threads.')

# scrape threads if not top of the month
threads_to_scrape = []
for submission in waywt_threads:
    if re.match('WAYWT\s[-_]\s\w+\s\d+', submission.title):
        threads_to_scrape.append(submission)


# get top comments from each thread
# ----------------------------------------
initialize_html(HTML_FILENAME)

# sort threads by date
threads_to_scrape.sort(key=lambda x: x.created, reverse=False)
all_top_comments = []
print('Beginning scraping.')
for thread in threads_to_scrape:
    # expand all comments, sort by top, and turn them into a list
    thread.comment_sort = 'top'
    thread.comments.replace_more(limit=0)
    comments = thread.comments.list()

    # we only want top-level comments
    top_level_comments = [c for c in comments if c.is_root]

    # scrape the first <COMMENTS_TO_SCRAPE> comments
    # probably 3, unless the top comment is a stickied mod comment
    n = 0
    for comment in top_level_comments:

        # don't want to write out stickied comments
        if comment.stickied:
            continue

        # add comment to list
        all_top_comments.append(comment)

        # only want the top 3 comments, not all of them
        n += 1
        if (n == COMMENTS_TO_SCRAPE):
            break

    print('Done with ' + thread.title)

# finished scraping and writing top comments to their individual divs
# now, write box for user to copy/paste code from
write_codebox(all_top_comments, HTML_FILENAME)

# write each comment to its own div
print 'Creating HTML file and saving images. Please wait.'
for i, comment in enumerate(all_top_comments):
    write_to_html(i, comment, HTML_FILENAME)
print 'Finished creating HTML file and saving images.'
print 'User notification of which images were unable to save is not completely working yet. Please make sure to manually check which images were unable to be saved.'

finalize_html(HTML_FILENAME)
print('Top posts from ' + month_to_scrape + ' written to ' + HTML_FILENAME)

# start the SimpleHTTPServer and open the webpage
PORT = 8000
Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
httpd = SocketServer.TCPServer(('', PORT), Handler)
print 'SimpleHTTPServer started. Serving to 0.0.0.0:' + str(PORT)
print 'When you are finished, close this terminal or press CTRL+C in this terminal to stop the SimpleHTTPServer.'
webbrowser.open('http://localhost:8000/')
httpd.serve_forever()
