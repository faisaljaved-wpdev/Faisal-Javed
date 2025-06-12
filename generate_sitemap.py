import os
os.makedirs("sitemaps", exist_ok=True)
import os
import re
import logging
from urllib.parse import urljoin
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree
import subprocess

# Configuration
SITE_URL = "https://faisaljaved.pro"
ROOT_DIR = "."
EXCLUDE_DIRS = {"node_modules", "venv", "env", ".git", ".next", "__pycache__", "public"}
SITEMAP_PATH = os.path.join("public", "sitemap.xml")
ROBOTS_PATH = os.path.join("public", "robots.txt")

# Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def is_valid_file(filename):
    return filename.endswith((".html", ".htm", ".php", ".pdf", ".jpg", ".jpeg", ".png", ".webp", ".mp4"))

def get_urls():
    urls = []
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for filename in filenames:
            if is_valid_file(filename):
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, ROOT_DIR).replace(os.sep, "/")
                if rel_path.startswith("public/"):
                    rel_path = rel_path[len("public/"):]
                url = urljoin(SITE_URL + "/", rel_path)
                urls.append(url)
    return urls

def generate_sitemap(urls):
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for url in sorted(set(urls)):
        url_element = SubElement(urlset, "url")
        loc = SubElement(url_element, "loc")
        loc.text = url
        lastmod = SubElement(url_element, "lastmod")
        lastmod.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    os.makedirs(os.path.dirname(SITEMAP_PATH), exist_ok=True)
    tree = ElementTree(urlset)
    tree.write(SITEMAP_PATH, encoding="utf-8", xml_declaration=True)
    logging.info(f"Sitemap written to {SITEMAP_PATH}")

def update_robots():
    robots_text = f"""User-agent: *
Disallow:

Sitemap: {SITE_URL}/sitemap.xml
"""
    os.makedirs(os.path.dirname(ROBOTS_PATH), exist_ok=True)
    with open(ROBOTS_PATH, "w") as f:
        f.write(robots_text)
    logging.info(f"robots.txt written to {ROBOTS_PATH}")

def git_push():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Update sitemap and robots.txt"], check=True)
        subprocess.run(["git", "push"], check=True)
        logging.info("Changes pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Git error: {e}")

def main():
    urls = get_urls()
    generate_sitemap(urls)
    update_robots()
    git_push()

if __name__ == "__main__":
    main()
