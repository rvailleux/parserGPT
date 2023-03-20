################################################################################
### Step 1
################################################################################
import getopt
import sys
import requests
import re
from bs4 import BeautifulSoup
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
import os

# Regex pattern to match a URL
HTTP_URL_PATTERN = r'^http[s]*://.+'

# Define root domain to crawl
full_url = ""
debug = False

try:
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv,"hu:d",["url=", "debug"])

    requirementMet = False

    for opt, arg in opts:
        if opt == '-h':
            print ('scraper.py -u <full_top_url>')
            sys.exit()
        elif opt in ("-u", "--url"):
            print("-u option detected : " + arg)
            full_url = arg
            requirementMet = True
        elif opt in ("-d", "--debug"):
            debug=True

    if not requirementMet:
        raise getopt.GetoptError("-u option mandatory.")

except getopt.GetoptError as e:
    print (e.msg + ' : scraper.py -u <full_top_url>')
    sys.exit(2)

domain = urlparse(full_url).netloc

if debug:
    print("Starting craxling URL: " +  full_url)
    print("Domain: " + domain)

""" 
# Create a class to parse the HTML and get the hyperlinks
class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        # Create a list to store the hyperlinks
        self.hyperlinks = []

    # Override the HTMLParser's handle_starttag method to get the hyperlinks
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # If the tag is an anchor tag and it has an href attribute, add the href attribute to the list of hyperlinks
        if tag == "a" and "href" in attrs:
            self.hyperlinks.append(attrs["href"])

################################################################################
### Step 2
################################################################################

# Function to get the hyperlinks from a URL
def get_hyperlinks(url):
    
    # Try to open the URL and read the HTML
    try:
        # Open the URL and read the HTML
        with urllib.request.urlopen(url) as response:

            # If the response is not HTML, return an empty list
            if not response.info().get('Content-Type').startswith("text/html"):
                return []
            
            # Decode the HTML
            html = response.read().decode('utf-8')
    except Exception as e:
        print(e)
        return []

    # Create the HTML Parser and then Parse the HTML to get hyperlinks
    parser = HyperlinkParser()
    parser.feed(html)

    return parser.hyperlinks

################################################################################
### Step 3
################################################################################

# Function to get the hyperlinks from a URL that are within the same domain
def get_domain_hyperlinks(local_domain, url):
    clean_links = []
    for link in set(get_hyperlinks(url)):
        clean_link = None

        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain:
                clean_link = link

        # If the link is not a URL, check if it is a relative link
        else:
            if link.startswith("/"):
                link = link[1:]
            elif link.startswith("#") or link.startswith("mailto:"):
                continue
            clean_link = "https://" + local_domain + "/" + link

        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))

 """

def logp(msg):
    if debug:
        print(msg)

def isurlvalid(targeturl, currenturl):

    if(not targeturl or not currenturl):
        raise ValueError("Undefined variable: targturl or currenturl")

    if(not re.compile('^' + targeturl, flags= re.I)):
        logp('Not matching the url pattern "^ '+targeturl+'" : ' + currenturl)
        return False
    
    if not currenturl.startswith(targeturl):
        logp('Not matching the url pattern "^ '+targeturl+'" : ' + currenturl)
        return False

    return True

def crawl(url):
    # Parse the URL and get the domain
    local_domain = domain

    # Create a queue to store the URLs to crawl
    queue = deque([url])

    # Create a set to store the URLs that have already been seen (no duplicates)
    seen = set([url])

    # Create a directory to store the text files
    if not os.path.exists("content/"):
            os.mkdir("content/")

    if not os.path.exists("content/"+local_domain+"/"):
            os.mkdir("content/" + local_domain + "/")

    # While the queue is not empty, continue crawling
    while queue:

        # Get the next URL from the queue
        url = queue.pop()
        print(url) # for debugging and to see the progress

        response = requests.get(url)

        if not response.headers['Content-Type'].startswith("text/html"):
            if debug:
                print("Not text/html: Skipping " + url)

            continue

        if response.is_redirect and not isurlvalid(response.url):
            if debug:
                print("Redirection out of targeted domain: Skipping " + url)

            continue

         # Get the text from the URL using BeautifulSoup
        soup = BeautifulSoup(response.text, "lxml")
        
        # Get the text but remove the tags
        text = str(soup.body)
       
        # Save text from the url to a <url>.txt file
        with open('content/'+local_domain+'/'+ str(hash(url[8:].replace("/", "_"))) + ".txt", "w", encoding="UTF-8") as f:
         
            # If the crawler gets to a page that requires JavaScript, it will stop the crawl
            if ("You need to enable JavaScript to run this app." in text):
                print("Unable to parse page " + url + " due to JavaScript being required")
            
            # Otherwise, write the text to the file in the text directory
            f.write(text)

        links = soup.find_all('a')

        if debug:
            print('Detected links: \n')
            for link in links:
                print(link.get('href'))

        # Get the hyperlinks from the URL and add them to the queue
        for link in links:
            href = link.get('href')

            if isurlvalid(full_url, href):
                if debug:
                    print("New url found >> " + href)

                queue.append(href)
                seen.add(href)

crawl(full_url)
