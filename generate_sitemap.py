import os
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree

# Config
SITE_URL = "https://faisaljaved.pro"
STATIC_PATHS = ["privacy-policy", "terms-of-service", "about"]
SAVE_DIR = "public"  # Directory where the sitemap will be saved
ROBOTS_PATH = os.path.join(SAVE_DIR, "robots.txt")
SITEMAP_PATH = os.path.join(SAVE_DIR, "sitemap.xml")

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def fetch_static_pages():
    urls = []
    for path in STATIC_PATHS:
        full_url = urljoin(SITE_URL + "/", path)
        urls.append(full_url)
    return urls


def crawl_page(url, visited):
    if url in visited or not url.startswith(SITE_URL):
        logging.info(f"Skipping URL {url} - already visited or not in domain")
        return []

    visited.add(url)
    urls = []

    try:
        logging.info(f"Crawling URL: {url}")
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all('a', href=True):
            href = link['href'].strip()

            if href.startswith("//"):
                href = "https:" + href
            elif not href.startswith("http"):
                href = urljoin(url, href)

            if href.startswith(SITE_URL) and href not in visited:
                urls.append(href)
                urls.extend(crawl_page(href, visited))

        return urls

    except Exception as e:
        logging.error(f"Error crawling {url}: {str(e)}")
        return []


def generate_sitemap(urls):
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for url in sorted(set(urls)):
        url_element = SubElement(urlset, "url")
        loc = SubElement(url_element, "loc")
        loc.text = url
        lastmod = SubElement(url_element, "lastmod")
        lastmod.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    tree = ElementTree(urlset)
    os.makedirs(SAVE_DIR, exist_ok=True)
    tree.write(SITEMAP_PATH, encoding="utf-8", xml_declaration=True)
    logging.info(f"Sitemap written to {SITEMAP_PATH}")


def update_robots():
    robots_text = f"""User-agent: *
Disallow:

Sitemap: {SITE_URL}/sitemap.xml
"""
    with open(ROBOTS_PATH, "w") as f:
        f.write(robots_text)
    logging.info(f"robots.txt written to {ROBOTS_PATH}")


def main():
    visited = set()
    all_urls = fetch_static_pages()
    all_urls.extend(crawl_page(SITE_URL, visited))
    generate_sitemap(all_urls)
    update_robots()


if __name__ == "__main__":
    main()
