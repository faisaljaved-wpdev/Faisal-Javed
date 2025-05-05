## Sitemap Generator Setup

1. **Files**:
   - `generate_sitemap.py`: Generates sitemaps (root folder).
   - `robots.txt`: Defines sitemap URL (root folder).
   - `.github/workflows/sitemap.yml`: Automates sitemap generation.

2. **GitHub Actions**:
   - Go to **Actions** tab and enable workflows.
   - Run the "Generate and Deploy Sitemap" workflow manually first.

3. **Generated Sitemaps**:
   - Check `/sitemap/` folder for:
     - `sitemap_index.xml`
     - `sitemap-pages.xml`
     - `sitemap-images.xml`
     - `sitemap-videos.xml`
     - `sitemap-pdfs.xml`
   - Visit `https://faisaljaved.pro/sitemap.xml`.

4. **Google Search Console**:
   - Submit `https://faisaljaved.pro/sitemap.xml` in Sitemaps section.

## Notes
- Sitemap auto-updates on every push.
- Dependencies (`requests`, `beautifulsoup4`, `lxml`) are handled by GitHub Actions.
