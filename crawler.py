from urllib.parse import urlparse, urljoin
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pymongo

class Frontier:
    def __init__(self, start_url):
        self.visited_urls = set()
        self.queue = [start_url]

    def done(self):
        return len(self.queue) == 0

    def next_url(self):
        if self.done():
            return None
        return self.queue.pop(0)

    def add_url(self, url):
        if url not in self.visited_urls:
            self.queue.append(url)
            self.visited_urls.add(url)


def retrieve_html(url):
    try:
        with urlopen(url) as response:
            return response.read()
    except Exception as e:
        print("Error retrieving {}: {}".format(url, e))
        return None


def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    return [link['href'] for link in links if link['href'].lower().endswith(('.html', '.shtml'))]


def target_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    for heading in headings:
        if heading.text.strip().lower() == "permanent faculty":
            return True
    return False


def store_page(url, html, collection):
    if html:
        collection.insert_one({'url': url, 'html': html.decode('utf-8')})


def crawler_thread(frontier, collection):
    while not frontier.done():
        url = frontier.next_url()
        html = retrieve_html(url)
        if html:
            store_page(url, html, collection)
            if target_page(html):
                frontier.queue.clear()
            else:
                for link in parse(html):
                    frontier.add_url(urljoin(url, link))


def main():
    start_url = "https://www.cpp.edu/sci/computer-science/"

    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["cs4250"]
    collection = db["pages"]

    frontier = Frontier(start_url)
    frontier.add_url(start_url)

    crawler_thread(frontier, collection)

    client.close()


if __name__ == "__main__":
    main()