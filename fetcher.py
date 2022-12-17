# dependencies that must be installed
from bs4 import BeautifulSoup
import praw
import sys
import re
import datetime
import http.server
import socketserver

# CONSTANTS
HTML_FILE = 'index.html'
COMMENTS_TO_SCRAPE = 3
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

def fetch_threads(month):
    reddit = praw.Reddit('waywtbot')
    mfa_subreddit = reddit.subreddit('malefashionadvice')

    # get all WAYWT threads for the month
    waywt_threads = mfa_subreddit.search('waywt ' + month, sort='new', syntax='lucene', time_filter='year')
    waywt_threads = [t for t in waywt_threads if re.match('WAYWT\s[-_](\s\w+\s\d+|\s\d+\s\w+)', t.title)]
    waywt_threads.sort(key=lambda x: x.created, reverse=False)

    top_submissions = []

    for thread in waywt_threads:

        # expand all comments, sort by top, and turn them into a list
        thread.comment_sort = 'top'
        thread.comments.replace_more(limit=0)
        comments = thread.comments.list()

        # we only want top-level comments that are not stickied
        top_level_comments = [c for c in comments if c.is_root and not c.stickied]

        # scrape the first <COMMENTS_TO_SCRAPE> comments -- probably 3
        for comment in top_level_comments[:COMMENTS_TO_SCRAPE]:
            top_submissions.append(comment)

        print('Done with ' + thread.title)

    return top_submissions


def initialize_html(filename):
    with open(filename, 'w+') as f:
        f.write('''<html>\n
        <head><title>Top of WAYWT</title><link rel="stylesheet" href="style.css"></head>\n
        <body>\n''')


# returns list of tuples of links in the format (link text, url)
def get_links(body_text):
    body_text = u''.join(body_text)

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


# writes <code> block to the html file specified by filename
def write_codebox(comments, filename):

    # file context manager for easy closing of file
    with open(filename, 'a') as f:
        f.write('''<div class="box1">\n
        <h3>Info Comment Markup</h3>\n
        <div class="code"><code>\n''')
        
        f.write('#How to call MFAImageBot:' + '<br /><br >\n' + '>\!MFA 2, 3, 42: I attempt to directly link the 2nd, 3rd, and 42nd images from the album in the submission' + '<br /><br >\n')

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


# finish off the html document
def finalize_html(filename):
    with open(filename, 'a') as f:
        f.write('</body>\n</html>')

# creates a div for each top post of the month in the html file
def write_comment(index, comment, filename):
    # convert unicode text
    links = get_links(comment.body)

    # convert seconds since epoch timestamp to proper date format
    fmt = "%B %d %Y"
    date = datetime.datetime.fromtimestamp(comment.created).strftime(fmt)

    # file context manager for easy closing of file
    with open(filename, 'a') as f:
        # write commenter /u/, permalink, and date to file
        f.write('<div class="box1">\n<h1>' + str(index) + '</h1>\n/u/' + str(comment.author) + '<br />\n')
        f.write('<a href="https://reddit.com' + str(comment.permalink) + '">Link to Comment</a><br />\n')
        f.write(date + '<br />\n<p></p>\n')

        if len(links) == 0:
            print('Unable to save image', str(index + 1))

        # write each link to file
        # if direct link to imgur image, write to <img> tag, otherwise to <a> tag
        for i, a in enumerate(links):
            text = a[0]
            url = a[1]

            # saves image if it's the first link in a post
            # if i == 0:
            #     save_image(url, str(index + 1))

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


def write_to_html(submissions):
    initialize_html(HTML_FILE)
    print('Writing submissions to html')
    write_codebox(submissions, HTML_FILE)
    for i, submission in enumerate(submissions):
        write_comment(i, submission, HTML_FILE)
    print('Finished creating HTML file and saving images.')
    print('User notification of which images were unable to save is not completely working yet. Please make sure to manually check which images were unable to be saved.')
    finalize_html(HTML_FILE)


def serve_html():
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print('Serving to 0.0.0.0:8000')
        print('When you are finished, close this terminal or press CTRL+C in this terminal to stop the server.')
        httpd.serve_forever()


if __name__ == "__main__":
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

    top_submissions = fetch_threads(month_to_scrape)
    write_to_html(top_submissions)
    serve_html()
