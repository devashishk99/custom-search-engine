import logging
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import json
from whoosh.fields import Schema, TEXT
from whoosh.analysis import CharsetFilter, StemmingAnalyzer
from whoosh.support.charset import accent_map
from indexer import index

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO
)

# adding an accent-folding filter to a stemming analyzer
analyser = StemmingAnalyzer() | CharsetFilter(accent_map)

## instantiating schema
schema = Schema(title=TEXT(stored=True, analyzer=analyser, spelling=True),
                topic=TEXT(stored=True, analyzer=analyser),
                link=TEXT(stored=True),
                body=TEXT(stored=True, analyzer=analyser))

## save data for later usage creating the file podcasts.txt.
def save_function(pod_list):
    with open('podcasts.txt', 'w+') as outfile:
        json.dump(pod_list, outfile)


class Spider:
    """
    Spider class for retrieving and parsing web content.

    Attributes:
    - url (str): The starting point for crawling.
    - urls_to_visit (list): The maximum depth to crawl, limiting how far into the website the crawler explores.
    - visited_urls (list): A set to keep track of visited URLs to avoid duplicate requests.
    - content (list): A list to store crawled data, typically in the form of dictionaries.

    Methods:
    - run(): Checks for the url to be visited and calls the crawl method.
    - crawl(base_url): Initiates the crawling process starting from the base_url which subsquently finds other urls.
    - download_url(url): Makes get request to url and returns the text response.
    - get_linked_urls(url, html): Parses through the html content and yeilds all links present in webpage.
    - add_url_to_visit(url): Adds the url to a list of 'should visit URLs' if it has not been visited yet.
    - get_content(link): Extracts relevant information from the link of a webpage.

    """
    
    def __init__(self, url):
        self.visited_urls = []
        self.urls_to_visit = [url]
        self.content = []

    def download_url(self, url):
        response = requests.get(url)
        response.raise_for_status()  
        return response.text

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)
            if re.match(r"https://www\.hubermanlab\.com/episode.[a-zA-Z0-9-_%=]*", str(url)) and 'timestamp' not in str(url):
                podcast_content = self.get_content(url)
                if podcast_content not in self.content:
                    self.content.append(podcast_content)
    
    def get_content(self, link):
        try:
            # merge all paragraphs to single string
            html_content = self.download_url(link)
            soup = BeautifulSoup(html_content,'html.parser')
            title = soup.find('h1', class_='h3').text
            notes = soup.find_all('div', class_='rich-text-episode-notes w-richtext')
            description = ''
            for n in notes:
                if n.find('p') is not None:
                    description = n.find('p').text          
            topic = soup.find('a', class_='chip-topics').text
            podcast = {
                'title': title,
                'link': link,
                'topic': topic,
                'description': description
                }

            return podcast
        except Exception:
            logging.exception('Could not extract content from HTML. Returning HTML text.')
            

    def crawl(self, url):
        html = self.download_url(url)
        for linked_url in self.get_linked_urls(url, html):
            if re.match(r"https://www\.hubermanlab\.com/(all-episodes|episode).[a-zA-Z0-9-_%=]*", str(linked_url)) and 'timestamp' not in str(linked_url):
                self.add_url_to_visit(linked_url)

    def run(self):
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)
            logging.info(f'Crawling: {url} ')
            try:
                self.crawl(url)
            except KeyboardInterrupt:
                print('\n'f'Keyboard Interrupt!')
                break
            except Exception as e:
                logging.exception(f'Failed to crawl: {url} - {e}')
            finally:
                self.visited_urls.append(url)

"""
1. The crawler is instantiated and it starts crawling from the starting url.
2. The scrapped content is saved.
3. Then it indexes the results.
"""
if __name__ == "__main__":
    url = 'https://www.hubermanlab.com/podcast'
    crawler = Spider(url)
    crawler.run()
    save_function(crawler.content)
    print(len(crawler.content))
    print('Finished crawling')
    print('Starting indexing')
    index(schema)
    print('Finished indexing')


