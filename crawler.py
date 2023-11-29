import logging
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import json
from whoosh.fields import Schema, TEXT
from whoosh.analysis import StemmingAnalyzer
from indexer import index

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO
)

## instantiating schema
schema = Schema(title=TEXT(stored=True),
                topic=TEXT(stored=True),
                link=TEXT(stored=True),
                body=TEXT(stored=True, analyzer=StemmingAnalyzer()))

## save data for later usage.
def save_function(pod_list):
    with open('podcasts.txt', 'w+') as outfile:
        json.dump(pod_list, outfile)


class Spider:
    """This class defines the skeleton of the crawler. First, it gets the
    HTML content of the given URL (dowland_url). Then it extracts the URLs
    by parsing the HTML content (get_linked_urls). Then it adds the URLs to 
    a list of 'should visit URLs' (add_url_to_visit). And finally fetches the
    content of the podcast (get_content)."""

    
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
            except requests.exceptions.RequestException as e:
                logging.error(f'Failed to crawl: {url} - {e}')
            except KeyboardInterrupt:
                print('\n'f'Keyboard Interrupt!')
                break
            except Exception as e:
                logging.exception(f'Failed to crawl: {url} - {e}')
            finally:
                self.visited_urls.append(url)


## It runs the crawler as a script and then indexes the results.
if __name__ == "__main__":
    url = 'https://www.hubermanlab.com/podcast'
    crawler = Spider(url)
    crawler.run()
    save_function(crawler.content)
    print('Finished crawling')
    print('Starting indexing')
    index(schema)
    print('Finished indexing')


