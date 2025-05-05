import os
import glob
import datetime
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
import git
import re

# Setup logging
logging.basicConfig(filename='sitemap.log', level=logging.INFO)

# Configuration
SITE_URL = "https://faisaljaved.pro"
LOCAL_PATH = "./"
SITEMAP_DIR = "./sitemap"
SITEMAP_INDEX_FILE = f"{SITEMAP_DIR}/sitemap_index.xml"
ROBOTS_FILE = "./robots.txt"
ALLOWED_EXTENSIONS = [".html", ".htm", ".php", ".asp"]
PING_URLS = [
    "https://www.google.com/ping?sitemap={}",
    "https://www.bing.com/ping?sitemap={}"
]

def ensure_sitemap_dir():
    if not os.path.exists(SITEMAP_DIR):
        os.makedirs(SITEMAP_DIR)
        logging.info(f"Created sitemap directory: {SITEMAP_DIR}")

def get_last_modified(file_path):
    try:
        return datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d')
    except:
        return datetime.datetime.now().strftime('%Y-%m-%d')

def get_change_frequency(url):
    if url == SITE_URL:
        return "weekly"
    elif "blog" in url:
        return "daily"
    else:
        return "monthly"

def get_priority(url):
    if url == SITE_URL:
        return "1.0"
    elif any(page in url for page in ["/skills", "/client_reviews", "/my_projects"]):
        return "0.9"
    else:
        return "0.5"

def crawl_page(url, visited):
    if url in visited or not url.startswith(SITE_URL):
        return []
    visited.add(url)
    urls = []
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = urljoin(url, link['href'])
            if href.startswith(SITE_URL) and href not in visited:
                urls.append(href)
                urls.extend(crawl_page(href, visited))
        return urls
    except Exception as e:
        logging.error(f"Error crawling {url}: {str(e)}")
        return []

def extract_images(soup, page_url):
    images = []
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src', '')  # Support lazy-loaded images
        src = urljoin(page_url, src)
        alt = img.get('alt', '')
        title = img.get('title', '')
        images.append({"src": src, "alt": alt, "title": title})
    return images

def extract_videos(soup, page_url):
    videos = []
    for video in soup.find_all(['video', 'iframe']):
        src = video.get('src') or video.get('data-src', '')
        src = urljoin(page_url, src)
        title = video.get('title', '')
        videos.append({"src": src, "title": title})
    return videos

def generate_page_sitemap(urls):
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url in urls:
        url_elem = ET.SubElement(urlset, "url")
        ET.SubElement(url_elem, "loc").text = url
        file_path = os.path.join(LOCAL_PATH, url.replace(SITE_URL, "").lstrip("/"))
        if os.path.exists(file_path):
            ET.SubElement(url_elem, "lastmod").text = get_last_modified(file_path)
        ET.SubElement(url_elem, "changefreq").text = get_change_frequency(url)
        ET.SubElement(url_elem, "priority").text = get_priority(url)
    return urlset

def generate_image_sitemap(urls):
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9", xmlnsimage="http://www.google.com/schemas/sitemap-image/1.1")
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            images = extract_images(soup, url)
            for img in images:
                url_elem = ET.SubElement(urlset, "url")
                ET.SubElement(url_elem, "loc").text = url
                image_elem = ET.SubElement(url_elem, "image:image")
                ET.SubElement(image_elem, "image:loc").text = img["src"]
                if img["alt"]:
                    ET.SubElement(image_elem, "image:caption").text = img["alt"]
                if img["title"]:
                    ET.SubElement(image_elem, "image:title").text = img["title"]
        except Exception as e:
            logging.error(f"Error generating image sitemap for {url}: {str(e)}")
    return urlset

def generate_video_sitemap(urls):
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9", xmlnsvideo="http://www.google.com/schemas/sitemap-video/1.1")
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            videos = extract_videos(soup, url)
            for video in videos:
                url_elem = ET.SubElement(urlset, "url")
                ET.SubElement(url_elem, "loc").text = url
                video_elem = ET.SubElement(url_elem, "video:video")
                ET.SubElement(video_elem, "video:content_loc").text = video["src"]
                if video["title"]:
                    ET.SubElement(video_elem, "video:title").text = video["title"]
        except Exception as e:
            logging.error(f"Error generating video sitemap for {url}: {str(e)}")
    return urlset

def generate_pdf_sitemap():
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for file_path in glob.glob(f"{LOCAL_PATH}/**/*.pdf", recursive=True):
        url = urljoin(SITE_URL, os.path.relpath(file_path, LOCAL_PATH).replace("\\", "/"))
        url_elem = ET.SubElement(urlset, "url")
        ET.SubElement(url_elem, "loc").text = url
        ET.SubElement(url_elem, "lastmod").text = get_last_modified(file_path)
        ET.SubElement(url_elem, "changefreq").text = "monthly"
        ET.SubElement(url_elem, "priority").text = "0.5"
    return urlset

def write_sitemap(urlset, filename):
    xmlstr = minidom.parseString(ET.tostring(urlset)).toprettyxml(indent="  ")
    with open(filename, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(xmlstr)
    logging.info(f"Generated sitemap: {filename}")

def generate_sitemap_index():
    sitemap_index = ET.Element("sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for sitemap_file in glob.glob(f"{SITEMAP_DIR}/*.xml"):
        if sitemap_file != SITEMAP_INDEX_FILE:
            sitemap = ET.SubElement(sitemap_index, "sitemap")
            ET.SubElement(sitemap, "loc").text = urljoin(SITE_URL, os.path.relpath(sitemap_file, LOCAL_PATH).replace("\\ frustrations, "/"))
            ET.SubElement(sitemap, "lastmod").text = get_last_modified(sitemap_file)
    return sitemap_index

def update_robots_txt():
    sitemap_url = urljoin(SITE_URL, "sitemap.xml")
    if os.path.exists(ROBOTS_FILE):
        with open(ROBOTS_FILE, "r") as f:
            content = f.read()
        if "Sitemap:" not in content:
            with open(ROBOTS_FILE, "a") as f:
                f.write(f"\nSitemap: {sitemap_url}\n")
    else:
        with open(ROBOTS_FILE, "w") as f:
            f.write(f"Sitemap: {sitemap_url}\n")
    logging.info("Updated robots.txt")

def ping_search_engines():
    sitemap_url = urljoin(SITE_URL, "sitemap.xml")
    for ping_url in PING_URLS:
        try:
            requests.get(ping_url.format(sitemap_url), timeout=5)
            logging.info(f"Pinged {ping_url.format(sitemap_url)}")
        except Exception as e:
            logging.error(f"Error pinging {ping_url.format(sitemap_url)}: {str(e)}")

def commit_and_push():
    try:
        repo = git.Repo(LOCAL_PATH)
        repo.git.add(SITEMAP_DIR)
        repo.git.add(ROBOTS_FILE)
        repo.index.commit("Update sitemap and robots.txt")
        repo.remotes.origin.push()
        logging.info("Committed and pushed changes")
    except Exception as e:
        logging.error(f"Error committing/pushing: {str(e)}")

def main():
    ensure_sitemap_dir()
    visited = set()
    urls = [SITE_URL]
    urls.extend(crawl_page(SITE_URL, visited))
    
    write_sitemap(generate_page_sitemap(urls), f"{SITEMAP_DIR}/sitemap-pages.xml")
    write_sitemap(generate_image_sitemap(urls), f"{SITEMAP_DIR}/sitemap-images.xml")
    write_sitemap(generate_video_sitemap(urls), f"{SITEMAP_DIR}/sitemap-videos.xml")
    write_sitemap(generate_pdf_sitemap(), f"{SITEMAP_DIR}/sitemap-pdfs.xml")
    write_sitemap(generate_sitemap_index(), SITEMAP_INDEX_FILE)
    
    update_robots_txt()
    ping_search_engines()
    commit_and_push()

if __name__ == "__main__":
    main()
